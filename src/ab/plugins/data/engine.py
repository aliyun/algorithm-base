from datetime import date, datetime
import dateutil
from pandas import DataFrame, Series
import pandas as pd

from ab import app

from ab.utils import logger
from ab.plugins.calculate import spark
from ab.utils.data_source import DataSource
from ab.plugins.db.odps_helper import ODPS
from ab.utils.exceptions import AlgorithmException


class Engine:
    @staticmethod
    def get_instance(config: dict = None):
        if not config or config['type'] == 'python':
            return Engine('python')
        if config['type'] == 'spark':
            return SparkEngine('spark')

    def __init__(self, _type):
        self._type = _type
        pass

    def read_data(self, ds: DataSource):
        """
        read data from data_source by engine
        :return: sample rate, sample count, DataFrame
        """
        sample_rate, sample_count, sample = ds.sample()
        table_info = ds.get_table_info()
        column_names = [c['field'] for c in table_info['columns']]
        sample_df = DataFrame(sample, columns=column_names)
        return sample_rate, sample_count, sample_df

    def read_data_by_sql(self, ds: DataSource):
        """
        read data from custom sql
        :param ds:
        :return:
        """

        # todo: extract field to DataFrame
        data = ds.data()
        return DataFrame(data)

    def stop(self):
        pass


class SparkEngine(Engine):
    @staticmethod
    def convert_boolean_type(rows, column_name):
        from pyspark.sql.types import BooleanType
        for row in rows:
            val = row[column_name]
            if val is None:
                continue
            if isinstance(val, bool):
                return rows, BooleanType()

        # convert 1/0 to True/False
        for row in rows:
            val = row[column_name]
            if val is None:
                continue
            row[column_name] = bool(val)
        return rows, BooleanType()

    @staticmethod
    def convert_date_type(rows, column_name):
        # https://spark.apache.org/docs/latest/sql-reference.html
        from pyspark.sql.types import StringType, IntegerType, DoubleType, TimestampType, DateType

        none_count = 0
        # try to verify date type without conversion
        for row in rows:
            val = row[column_name]
            if val is None:
                none_count += 1
                continue
            # pd.Timestamp is subclass of datetime, but....spark don't understand
            # have to convert it
            if isinstance(val, pd.Timestamp):
                break
            # datetime is subclass of date
            if isinstance(val, datetime):
                return rows, TimestampType()
            if isinstance(val, date):
                return rows, DateType()
            if isinstance(val, int):
                # perhaps for timestamp or interval?
                return rows, IntegerType()
            if isinstance(val, float):
                # perhaps for timestamp or interval?
                return rows, DoubleType()
        if none_count == len(rows):
            # all None, any type is ok
            return rows, TimestampType()

        try:
            # convert to datetime
            for row in rows:
                val = row[column_name]
                if val is None:
                    continue
                if isinstance(val, pd.Timestamp):
                    row[column_name] = val.to_pydatetime()
                else:
                    row[column_name] = dateutil.parser.parse(str(row[column_name]), fuzzy=True)
            return rows, TimestampType()
        except Exception as e:
            # fallback to string
            for row in rows:
                val = row[column_name]
                if val is None or isinstance(val, str):
                    continue
                row[column_name] = str(row[column_name])
            return rows, StringType()

    @staticmethod
    def convert_to_spark_data_type(sample, table_info):
        from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DoubleType, \
            TimestampType, DateType
        mapping = {
            'String': StringType(),
            'Long': IntegerType(),
            'Double': DoubleType(),
            # Boolean and Date fields should be further analyzed
        }

        fields = []
        columns = table_info['columns']
        for c in columns:
            cname = c['field']
            xt = c['xlabType']
            if xt == 'Date':
                sample, spark_type = SparkEngine.convert_date_type(sample, cname)
            elif xt == 'Boolean':
                sample, spark_type = SparkEngine.convert_boolean_type(sample, cname)
            else:
                spark_type = mapping[xt]
            fields.append(StructField(cname, spark_type, True))
        spark_dataframe = spark.get_or_create().createDataFrame(sample, schema=StructType(fields))
        return spark_dataframe

    def read_data(self, ds: DataSource):
        # local mode, force sampling
        if app.config.SPARK['spark.master'].startswith('local'):
            sample_rate, sample_count, sample = ds.sample()
            spark_dataframe = self.convert_to_spark_data_type(sample, ds.get_table_info())
            return sample_rate, sample_count, spark_dataframe

        # else load all data
        if ds.type_ in ('mysql', 'ads'):
            return 100, None, spark.get_or_create().read.format('jdbc') \
                .option('url', ds.db.jdbc_url) \
                .option('driver', 'com.mysql.jdbc.Driver') \
                .option('dbtable', ds.table_name) \
                .option('user', ds.db.username) \
                .option('password', ds.db.password) \
                .option('useUnicode', True) \
                .option('characterEncoding', 'UTF-8') \
                .load()
        elif ds.type_ == 'hive':
            sql = 'SELECT * FROM {db}.{table_name}'.format(db=ds.db.db, table_name=ds.table_name)
            if ds.partitions:
                condition = ODPS.join_partitions(ds.partitions)
                sql += ' where {condition}'.format(condition=condition)
            logger.info('sample sql:', sql)
            return 100, None, spark.get_or_create().sql(sql)
        elif ds.type_ == 'odps':
            if not ds.db.tunnel_endpoint:
                raise AlgorithmException('please set odps tunnel endpoint')
            # cluster mode, read all data
            data = spark.get_or_create().read \
                .format("org.apache.spark.aliyun.odps.datasource") \
                .option("odpsUrl", ds.db.endpoint) \
                .option("tunnelUrl", ds.db.tunnel_endpoint) \
                .option("table", ds.table_name) \
                .option("project", ds.db.project) \
                .option("accessKeyId", ds.db.access_id) \
                .option("accessKeySecret", ds.db.access_key)
            num_partitions = spark.get_or_create().sparkContext.getConf().get('odps.numPartitions')
            if num_partitions:
                data = data.option("numPartitions", int(num_partitions))
            if ds.partitions:
                assert len(ds.partitions) == 1, 'spark can only read one odps partition'
                data = data.option('partitionSpec', ds.partitions[0])
            return 100, None, data.load()
        raise AlgorithmException('unrecognized data source type for spark: {ds.type_}'.format(ds=ds))

    def stop(self):
        spark.stop()
