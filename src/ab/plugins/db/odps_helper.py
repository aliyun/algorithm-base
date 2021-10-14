from ab.utils.prometheus import func_metrics
from odps import ODPS as _ODPS
from odps.errors import ODPSError
from odps import options

from ab import app
from ab.utils import logger
from ab.plugins.db.base import DataBase
from ab.utils.exceptions import AlgorithmException


class ODPS(DataBase):
    @staticmethod
    def record_to_dict(record):
        """
        odps Record to dict
        """
        return {r[0]: r[1] for r in record}

    def __init__(self, access_id, access_key, project, endpoint=None, tunnel_endpoint=None, log_view_host=None, debug=False):
        self.sampler_class = Sampler
        self.access_id = access_id
        self.access_key = access_key
        self.project = project
        self.endpoint = endpoint
        self.tunnel_endpoint = tunnel_endpoint
        self.log_view_host = log_view_host
        self.odps = _ODPS(access_id, access_key, project, endpoint=endpoint)
        self.debug = debug

        # http://pyodps.alibaba.net/pyodps-docs/zh-CN/latest/options.html
        options.verbose = debug
        options.sql.use_odps2_extension = True
        options.sql.settings = {
            'odps.sql.allow.fullscan': True
        }

        # 更换项目空间
        # odps = odps.get_project(project)

    def get_config(self):
        return {
            'access_id': self.access_id,
            'access_key': self.access_key,
            'project': self.project,
            'endpoint': self.endpoint,
            'log_view_host': self.log_view_host
        }

    def table(self, table_name):
        return self.odps.get_table(table_name)

    @func_metrics('odps_execute')
    def execute(self, sql: str, step=1000):
        """
        execute sql,
            select return list of dict
            else return reader.raw
        """
        with self.odps.execute_sql(sql).open_reader() as reader:
            if hasattr(reader, 'count'):
                count = reader.count
                i = 0
                records = []
                while i < count:
                    records.extend(reader[i: min(count, i + step)])
                    i += step
                return [ODPS.record_to_dict(r) for r in records]
            return reader.raw

    def column_names(self, table_name):
        table = self.table(table_name)
        schema = table.schema
        # columns = [{'field': c.name, 'type': c.type.name, 'xlabType': odps_to_xlab_type(c.type), 'comment': c.comment}
        #             for c in schema.columns]
        return [c.name for c in schema.columns]

    def partitions_inner(self, table_name) -> list:
        """
        returns odps parition raw type, DO NOT invoke this directly
        returns:
            None: not a partitioned table
            []: no data
            [p1 object, p2 object]. use p.name to get partition string
        """
        table = self.odps.get_table(table_name)
        if table.schema.partitions:
            # is partitioned table
            logger.debug('get partitions', [p.name for p in table.partitions])
            return list(table.partitions)
        else:
            return None

    def partitions(self, table_name) -> list:
        """
        return all partitions string
        returns:
            None: not a partitioned table
            []: no data
            ['p1=v1,p2=v2', 'p1=v3,p2=v4']
        """
        partitions = self.partitions_inner(table_name)
        if not partitions:
            return partitions
        return [partition.name for partition in partitions]

    def level_one_partition_key(self, table_name) -> str:
        """
        :return:
            None: not a partitioned table
            '': no data
            'p1'
        """
        partitions = self.partitions(table_name)
        if partitions is None:
            return None
        if partitions == []:
            return ''
        return partitions[-1].split(',')[0].split('=')[0]

    def max_partition(self, table_name) -> str:
        """
        returns the alphabetically maximum LEVEL ONE partition which has data
        returns:
            None: not a partitioned table
            '': no data
            'p1="v1"'
        """
        table = self.table(table_name)
        if not table.schema.partitions:
            return None

        sql = 'select max_pt("{table_name}") as mp from {table_name};'.format(table_name=table_name)
        try:
            with self.odps.execute_sql(sql).open_reader() as reader:
                partition_key = self.level_one_partition_key(table_name)
                partition_value = reader[0]['mp']
                return '{partition_key}="{partition_value}"'.format(
                    partition_key=partition_key, partition_value=partition_value)
        except ODPSError as e:
            if 'none of the partitions have any data' in str(e):
                return ''
            raise

    def get_partition_condition(self, table_name, _type='all') -> str:
        """
        args:
            _type:
                all: all partitions considered
                max: only use the max_partition(table_name)
        returns:
            None: not a partitioned table
            '': no data
            '(p1=v1 and p2=v2) or (p1=v3 and p2=v4)'
        """
        if _type == 'all':
            partitions = self.partitions(table_name)
        elif _type == 'max':
            partition = self.max_partition(table_name)
            if partition:
                partitions = [partition, ]
            else:
                partitions = partition
        return ODPS.join_partitions(partitions)

    @staticmethod
    def join_partitions(partitions: list) -> str:
        """
        join partitions into where conditions
        input:
            None
            []
            ['p1=v1/p2=v2', 'p1=v3/p2=v4'] or ['p1=v1,p2=v2', 'p1=v3,p2=v4']
        returns:
            None: not a partitioned table
            '': no data
            '((p1='v1' and p2='v2') or (p1='v3' and p2='v4'))'
        """
        if partitions is None:
            return None
        elif not partitions:
            return ''
        else:
            # partitions: ['p1=v1/p2=v2', yyy] ->
            #     p: 'p1=v1/p2=v2' ->
            #     kv_pairs: ['p1=v1', 'p2=v2'] ->
            #         kv_pair: 'p1=v1' ->
            #             k: p1   v: 'v1' ->
            #     quoted_kv_pairs: ["p1='v1'", "p2='v2'"] ->
            # partition_strings: ["p1='v1' and p2='v2'"] ->
            # return ((p1='v1' and p2='v2') or (yyy))

            partition_strings = []
            for p in partitions:
                # odps does not allow '/' or ',' in partition keys, just split
                if '/' in p:
                    kv_pairs = p.split('/')
                elif ',' in p:
                    kv_pairs = p.split(',')
                else:
                    kv_pairs = [p, ]

                quoted_kv_pairs = []
                for kv_pair in kv_pairs:
                    k, v = kv_pair.split('=')
                    if "'" not in v and '"' not in v:
                        # convert string partition key. bigint key compatible
                        v = "'{v}'".format(v=v)
                    quoted_kv_pairs.append('{k}={v}'.format(k=k, v=v))
                partition_strings.append(' and '.join(quoted_kv_pairs))

            return '((' + ') or ('.join(partition_strings) + '))'

    def execute_sql_cost(self, sql: str):
        """
        https://help.aliyun.com/document_detail/112752.html?spm=a2c4g.11186623.2.10.19f443d6o09jYR#concept-odj-bjq-fhb
        一次SQL计算费用 = 计算输入数据量 * SQL复杂度 * 单价（0.3元/GB）
        """
        try:
            cost = self.odps.execute_sql_cost(sql)
            return (cost.input_size / (1024 ** 3)) * cost.complexity * 0.3
        except:
            # pyodps<=0.8.3
            # odps.errors.ODPSError: InstanceId: 20190903065133805gv7vqmim
            # ODPS-0140181:Sql plan exception - sql cost error:ODPS-0130151:Illegal data type - Column 'ti' type 'tinyint' is not allowed.
            return 0

    def count(self, table_name, partitions=None, skip_high_cost_query=True, cost_threshold=30):
        """
        :param table_name:
        :param partitions:
        :param skip_high_cost_query: if table or table partition is too large,
                                 or the query is too complex,
                                 it may takes too long to count every line.
                                 return None instead
        :param cost_threshold: default is 30 RMB, for counting 100GB data
        :return:
            None: table too large, skip count
            >=0: real count
        """
        if partitions is None:
            partition_condition = self.get_partition_condition(table_name)
        else:
            partition_condition = ODPS.join_partitions(partitions)

        if partition_condition == '':
            return 0

        if partition_condition is None:
            sql = 'select count(*) as count from {table_name}'.format(table_name=table_name)
        else:
            sql = 'select count(*) as count from {table_name} where {partition_condition}'.format(
                table_name=table_name, partition_condition=partition_condition)

        cost = self.execute_sql_cost(sql)
        if skip_high_cost_query and cost > cost_threshold:
            return None

        with self.odps.execute_sql(sql).open_reader() as reader:
            return reader[0]['count']

    def select(self, table_name, limit=None, step=1000):
        if not table_name:
            return None

        table = self.odps.get_table(table_name)

        ret = []
        with table.open_reader() as reader:
            count = reader.count
            if limit:
                count = min(count, limit)
            i = 0
            while i < count:
                for r in reader[i: min(count, i + step)]:
                    ret.append(r)
                i += step
        return ret

    def xselect(self, table_name, limit=None, step=1000):
        if not table_name:
            return None

        table = self.odps.get_table(table_name)

        with table.open_reader() as reader:
            count = reader.count
            if limit:
                count = min(count, limit)
            i = 0
            while i < count:
                yield reader[i: min(count, i + step)]
                i += step

    def insert(self, table_name, records: list, **kwargs) -> None:
        """
        :param table_name:
        :param records: [[column_1_value, column_2_value...], ]
                        or
                        [{column_1_name: column_1_value, column_2_name: column_2_value...}]
        :param kwargs: see odps table.open_writer args
        """
        column_names = self.column_names(table_name)
        record_list = []
        for record in records:
            if isinstance(record, list):
                record_list.append(record)
            elif isinstance(record, dict):
                record_list.append([record.get(c, None) for c in column_names])

        table = self.odps.get_table(table_name)
        with table.open_writer(**kwargs) as writer:
            writer.write(record_list)

    def run_security_query(self, query: str):
        return self.odps.run_security_query(query)

    def create_user(self, name: str):
        return self.odps.create_user(name)

    def sample(self, table_name, partitions=None):
        """
        sample max_pt(table_name)
        args:
            self.max_count: rows to be returned at most
            partitions: ['p1=v1/p2=v2']

        returns:
            sample_rate: if table is too large, sample_rate will be None
            sample_count,
            sample_data
        """
        column_names = self.column_names(table_name)

        if partitions is None:
            max_pt = self.max_partition(table_name)
            if max_pt == '':
                # no data
                return 100, 0, []
            elif max_pt is None:
                # not a partitoned table, full scan
                partitions = None
            else:
                # use max_pt as default
                partitions = [max_pt, ]

        total_count = self.count(table_name, partitions)
        # TODO is max_count common among samplers?
        if total_count is not None and total_count <= self.sampler.max_count:
            # return full set, no sampling
            partition_condition = ODPS.join_partitions(partitions)
            where = (' where ' + partition_condition) if partition_condition else ''
            sql = 'select * from {table_name}{where}'.format(table_name=table_name, where=where)

            logger.debug('total_count: {total_count}, max_count: {self.sampler.max_count}'.format(
                total_count=total_count, self=self))
            logger.debug('no need to sample, run sql:', sql)
            return 100, total_count, self.table_sql(sql, table_name, column_names)

        sample = self.sampler.sample(table_name, column_names, partitions, total_count)
        sample_count = len(sample)
        sample_rate = 100.0 * sample_count / total_count if total_count else None
        return sample_rate, sample_count, sample

    @staticmethod
    def odps_to_xlab_type(data_type):
        """
        MaxCompute 2.0 new data types:
        http://help.aliyun-inc.com/internaldoc/detail/27821.html
        """
        _type = str(data_type).lower()
        if any(string_type in _type for string_type in ['string', 'varchar']):
            return 'String'
        elif 'int' in _type:
            return 'Long'
        elif _type == 'boolean':
            return 'Boolean'
        elif any(float_type in _type for float_type in ['float', 'double', 'decimal']):
            return 'Double'
        elif any(date_type in _type for date_type in ['date', 'time']):
            return 'Date'
        else:
            raise TypeError('不支持的odps数据类型: {_type}'.format(_type=_type))

    def table_info(self, table_name, with_row_count=False):
        '''
        returns table info in db
        returns: {
            'type': data source type,
            'size': table size in KB,
            'row_count': row count in db, optional,
            'columns': [
                    {'field': 'name', 'type': 'varchar(100)', 'xlabType': 'String', 'comment': '公司名称'},
                    {'field': 'f1', 'type': 'double', 'xlabType': 'Double', comment': '年总销售额'}
                ]
            'partitions': ['p1=v1/p2=v2']
        '''
        table = self.table(table_name)
        schema = table.schema
        columns = [{'field': c.name, 'type': c.type.name, 'comment': c.comment,
                    'xlabType': self.odps_to_xlab_type(c.type),
                    }
                   for c in schema.columns]
        partitions = self.partitions(table_name)
        ret = {
            'type': 'odps',
            'size': table.size / 1024,
            # 'psy_size': table.physical_size,
            'columns': columns,
            'partitions': partitions
        }
        if with_row_count:
            ret['row_count'] = self.count(table_name)
        return ret


class Sampler:
    @staticmethod
    def get_instance(db: ODPS, config: dict):
        """
        args:
            config: {
                'type': random/head/tail/column_variety_random,
                'count': max sample size
                }
        """
        config = app.config.FORCE_SAMPLER or config or app.config.SAMPLER

        assert isinstance(config.get('count'), int) and config['count'] > 0, \
            'sampler.count must be positive integer, not string'

        if config['type'] == 'random':
            return RandomSampler(db, config)
        elif config['type'] == 'head':
            return HeadSampler(db, config)
        elif config['type'] == 'tail':
            return TailSampler(db, config)
        elif config['type'] == 'column_variety_random':
            return ColumnVarietyRandomSampler(db, config)
        else:
            raise ValueError('unknown sampler type:', config['type'])

    def __init__(self, db: ODPS, config: dict):
        self.db = db
        self._type = config['type']
        self.max_count = config['count']
        self.debug = db.debug

    @property
    def key(self):
        return '{self._type}.{self.max_count}'.format(self=self)


class RandomSampler(Sampler):
    def sample(self, table_name: str, column_names: list, partitions: list, total_count: int):
        """
        args:
            total_count: total row count of target partitions or whole table
        returns:
            sample_data
        """
        if total_count is None:
            raise AlgorithmException(data='选择的表过大，仅支持最旧采样')

        assert total_count > self.max_count, 'system error, total_count must be greater than sampler max_count'

        condition = ODPS.join_partitions(partitions)

        ratio = total_count // self.max_count
        sample_condition = 'sample({ratio}) = true'.format(ratio=ratio)
        if condition:
            condition = '({condition}) and {sample_condition}'.format(condition=condition, sample_condition=sample_condition)
        else:
            condition = sample_condition

        if condition:
            where = ' where {condition}'.format(condition=condition)
        else:
            where = ''

        fields = ', '.join(column_names)
        sql = 'select {fields} from {table_name}{where} limit {self.max_count}'.format(
            fields=fields, table_name=table_name, where=where, self=self)

        logger.debug('sample sql:', sql)
        return self.db.table_sql(sql, table_name, column_names)


class HeadSampler(Sampler):
    """
    return head rows
    """

    def sample(self, table_name: str, column_names: list, partitions: list, total_count: int):
        """
        args:
            total_count: total row count of target partitions or whole table
        returns:
            sample_data
        """
        assert total_count is None or total_count > self.max_count, 'system error, total_count must be greater than sampler max_count'

        condition = ODPS.join_partitions(partitions)
        if condition:
            where = ' where {condition}'.format(condition=condition)
        else:
            where = ''

        fields = ', '.join(column_names)
        sql = 'select {fields} from {table_name}{where} limit {self.max_count}'.format(
            fields=fields, table_name=table_name, where=where, self=self
        )

        logger.debug('sample sql:', sql)
        return self.db.table_sql(sql, table_name, column_names)


class TailSampler(Sampler):
    """
    return tail rows
    """

    def sample(self, table_name: str, column_names: list, partitions: list, total_count: int):
        """
        args:
            total_count: total row count of target partitions or whole table
        returns:
            sample_data
        """
        if total_count is None:
            raise AlgorithmException(data='选择的表过大，仅支持最旧采样')

        assert total_count > self.max_count, 'system error, total_count must be greater than sampler max_count'

        condition = ODPS.join_partitions(partitions)
        if condition:
            inner_where = ' where {condition}'.format(condition=condition)
        else:
            inner_where = ''

        fields = ', '.join(column_names)
        sql = """select {fields} from 
                    (select {fields}, row_number() over (partition by 1) as _xlab_tail_sampling_row_number from {table_name}{inner_where}) a
                where _xlab_tail_sampling_row_number > {rn}""".format(
            fields=fields, table_name=table_name, inner_where=inner_where, rn=total_count - self.max_count
        )

        logger.debug('sample sql:', sql)
        return self.db.table_sql(sql, table_name, column_names)


class ColumnVarietyRandomSampler(Sampler):
    """
    ensure every distinct value of self.column_name appears in result
    """

    def __init__(self, db, config: dict):
        super().__init__(db, config)
        self.column_name = config['column_name']

    @property
    def key(self):
        return '{self._type}.{self.column_name}.{self.max_count}'.format(self=self)

    def sample(self, table_name: str, column_names: list, partitions: list, total_count: int):
        """
        args:
            total_count: total row count of target partitions or whole table
        returns:
            sample_data
        """
        if total_count is None:
            raise AlgorithmException(data='选择的表过大，仅支持最旧采样')

        assert total_count > self.max_count, 'system error, total_count must be greater than sampler max_count'

        fields = ', '.join(column_names)
        condition = ODPS.join_partitions(partitions)
        if condition:
            where = 'where {condition}'.format(condition=condition)
        else:
            where = ''

        ratio = total_count // self.max_count
        sql = '''select {fields} from 
                        (select 
                            {fields}, 
                            cluster_sample({ratio}, 1) over (partition by {self.column_name}) as _column_variety_random_sampler_flag,
                            row_number() over (partition by {self.column_name}) as _column_variety_random_sampler_row_number
                            from {table_name}
                            {where}
                            ) a
                  where _column_variety_random_sampler_flag = true
                  order by _column_variety_random_sampler_row_number
                  limit {self.max_count}
                '''.format(fields=fields, ratio=ratio, self=self, table_name=table_name, where=where)

        logger.debug('sample sql:', sql)
        return self.db.table_sql(sql, table_name, column_names)
