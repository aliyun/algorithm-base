from ab.utils import data_source
from ab.utils.algorithm import Algorithm
from ab.plugins.data.engine import Engine


# todo: 还未使用的类
class DataReader():
    @staticmethod
    def enabled():
        # always enabled
        return True

    def pre_run(self, algorithm: Algorithm, request: dict, kwargs: dict):
        if not request.get('data_source') or not ('data' in algorithm.params or 'table_info' in algorithm.params):
            return

        self.engine = Engine.get_instance(request.get('engine'))
        self.ds_instance_list = []
        data_list = []
        sr_list = []
        sc_list = []
        ti_list = []
        for ds in request['data_source']:
            ds_instance = data_source.DataSource.get_instance_by_id(ds['id'], ds['table_name'], ds.get('partitions'))
            self.ds_instance_list.append(ds_instance)
            if 'data' in algorithm.params:
                sample_rate, sample_count, data = self.engine.read_data(ds_instance)
                sr_list.append(sample_rate)
                sc_list.append(sample_count)
                data_list.append(data)
            # get table meta from db
            if 'table_info' in algorithm.params:
                table_info = self.data_source.get_table_info()
                ti_list.append(table_info)

        if len(request['data_source']) == 1:
            # only one data source, unpack
            kwargs['data'] = data_list[0]
            kwargs['sample_rate'] = sr_list[0]
            kwargs['sample_count'] = sc_list[0]
            kwargs['table_info'] = ti_list[0]
        else:
            # multiple data source, return as list
            kwargs['data'] = data_list
            kwargs['sample_rate'] = sr_list
            kwargs['sample_count'] = sc_list
            kwargs['table_info'] = ti_list

    def post_run(self, response):
        if hasattr(self, 'ds_instance_list'):
            for ds_instance in self.ds_instance_list:
                ds_instance.close()
        if hasattr(self, 'engine'):
            self.engine.stop()
