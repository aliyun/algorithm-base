import decimal
import sys
import pickle
from datetime import date, datetime

import numpy
import pandas as pd
import simplejson as json
from werkzeug.datastructures import FileStorage

from ab.utils.prometheus import func_metrics


class AlgorithmEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, pd.DataFrame):
            return o.to_dict('records')
        if isinstance(o, pd.Series):
            return o.tolist()
        if isinstance(o, numpy.integer):
            return int(o)
        if isinstance(o, decimal.Decimal):
            try:
                # may fail
                io = int(o)
                if io == o:
                    return io
            except:
                pass
            return float(o)
        if isinstance(o, pd.Timestamp):
            # convert microsecond to millisecond
            return o.strftime('%Y-%m-%d %H:%M:%S') + '.{:03d}'.format(int(o.microsecond / 1000))
        if isinstance(o, numpy.ndarray):
            return o.tolist()
        if isinstance(o, pd._libs.tslibs.nattype.NaTType):
            # null date
            return None
        # NaT is subtype of datetime
        if isinstance(o, datetime):
            if sys.version_info >= (3, 6, 0):
                return o.isoformat(sep=' ', timespec='milliseconds')
            else:
                ret = o.isoformat(sep=' ')
                if not ret:
                    return ret
                return ret + '.000'
        # date is super class of datetime, so process later
        if isinstance(o, date):
            return str(o)
        try:
            from pyspark.sql import DataFrame as SparkDataFrame
            if isinstance(o, SparkDataFrame):
                # could be slow
                return o.toPandas().to_dict('records')
        except ImportError:
            pass
        if isinstance(o, FileStorage):
            return 'file context not saved'
        return super(AlgorithmEncoder, self).default(o)


@func_metrics('serializer_dumps')
def dumps(obj, *args, **kwargs):
    """json string"""
    return json.dumps(obj, *args, **kwargs, ensure_ascii=False, ignore_nan=True, cls=AlgorithmEncoder)


def loads(s, *args, **kwargs):
    """
    handles bin data like a charm
    """
    return json.loads(s, *args, **kwargs, encoding='utf8')


def dumps_bin(obj, *args, **kwargs):
    """
    binary
    can't dump spark DataFrame
    """
    return pickle.dumps(obj, *args, **kwargs)


def loads_bin(binary, *args, **kwargs):
    return pickle.loads(binary, *args, **kwargs)
