from datetime import date, datetime
import dateutil
from pandas import DataFrame, Series
import pandas as pd

from ab import app

from ab.utils import logger
from ab.utils.data_source import DataSource
from ab.utils.exceptions import AlgorithmException


class Engine:
    @staticmethod
    def get_instance(config: dict = None):
        if not config or config['type'] == 'python':
            return Engine('python')

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

