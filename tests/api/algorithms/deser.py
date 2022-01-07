from ab.utils.algorithm import algorithm
import numpy


@algorithm()
def response_type():
    return [1, 1.1, numpy.int(1), numpy.int64(2), numpy.float(3.0), numpy.float64(4.0)]
