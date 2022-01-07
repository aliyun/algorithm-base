import decimal
import sys
import pickle
from datetime import date, datetime
from flask import Response

import numpy
import pandas as pd
import simplejson as json
from werkzeug.datastructures import FileStorage

from ab.utils.prometheus import func_metrics

from functools import singledispatch


_cant_serialize = dict()

@singledispatch
def json_serializable(object, skip_underscore=False):
    """Filter a Python object to only include serializable object types

    In dictionaries, keys are converted to strings; if skip_underscore is true
    then keys starting with an underscore ("_") are skipped.

    """
    # default handler, called for anything without a specific
    # type registration.
    return object


@json_serializable.register(dict)
def _handle_dict(d, skip_underscore=False):
    converted = ((str(k), json_serializable(v, skip_underscore))
                 for k, v in d.items())
    if skip_underscore:
        converted = ((k, v) for k, v in converted if k[:2] != '__')
    return {k: v for k, v in converted if v is not _cant_serialize}


@json_serializable.register(list)
@json_serializable.register(tuple)
def _handle_sequence(seq, skip_underscore=False):
    converted = (json_serializable(v, skip_underscore) for v in seq)
    return [v for v in converted if v is not _cant_serialize]

@json_serializable.register(int)
@json_serializable.register(float)
@json_serializable.register(str)
@json_serializable.register(bool)  # redudant, supported as int subclass
@json_serializable.register(type(None))
@json_serializable.register(numpy.bool)
@json_serializable.register(numpy.bool_)
@json_serializable.register(numpy.int)
@json_serializable.register(numpy.int_)
@json_serializable.register(numpy.intc)
@json_serializable.register(numpy.intp)
@json_serializable.register(numpy.int8)
@json_serializable.register(numpy.int16)
@json_serializable.register(numpy.int32)
@json_serializable.register(numpy.int64)
@json_serializable.register(numpy.uint8)
@json_serializable.register(numpy.uint16)
@json_serializable.register(numpy.uint32)
@json_serializable.register(numpy.uint64)
@json_serializable.register(numpy.float_)
@json_serializable.register(numpy.float)
@json_serializable.register(numpy.float16)
@json_serializable.register(numpy.float32)
@json_serializable.register(numpy.float64)
@json_serializable.register(numpy.complex)
@json_serializable.register(numpy.complex_)
@json_serializable.register(numpy.complex64)
@json_serializable.register(numpy.complex128)
def _handle_default_scalar_types(value, skip_underscore=False):
    return value


class AlgorithmEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Response):
            return str(o.data)
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
    serialize_obj = json_serializable(obj, skip_underscore=True)
    return json.dumps(serialize_obj, *args, **kwargs, ensure_ascii=False, ignore_nan=True, cls=AlgorithmEncoder)


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
