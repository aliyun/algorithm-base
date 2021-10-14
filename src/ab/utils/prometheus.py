"""
some generic prometheus metrics
"""
import functools
import inspect

from prometheus_client import Counter, Histogram
from prometheus_client.metrics import Gauge

c_http_requests = Counter("http_requests_total", "http requests in all", labelnames=['app', 'method', 'url', 'code'])
h_http_request_duration_seconds = Histogram("http_request_duration_seconds", "http request duration",
                                            labelnames=['app', 'method', 'url'])
g_inprogress_http_requests = Gauge("inprogress_http_requests", "help", labelnames=['app', 'method', 'url'],
                                   multiprocess_mode='livesum')


def http_metrics():
    """works within routes"""

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            from ab import request
            method = request.method
            url = request.path
            # count errors

            from ab import app
            app_name = app.config['APP_NAME']

            with c_http_requests.labels(app=app_name, method=method, url=url, code=500).count_exceptions():
                # accumulate inprogress
                with g_inprogress_http_requests.labels(app=app_name, method=method, url=url).track_inprogress():
                    # calculate time
                    with h_http_request_duration_seconds.labels(app=app_name, method=method, url=url).time():
                        ret = func(*args, **kwargs)
            # count success
            c_http_requests.labels(app=app_name, method=method, url=url, code=200).inc()
            return ret

        return inner

    return wrapper


c_func_errors = Counter('func_call_errors_total', 'error of funcs', labelnames=['app', 'name'])
c_func_calls = Counter("func_calls_total", "func call in all", labelnames=['app', 'name'])
h_func_call_duration_seconds = Histogram("func_call_duration_seconds", "func call duration",
                                         labelnames=['app', 'name'])
g_inprogress_func_calls = Gauge("inprogress_func_calls", "help", labelnames=['app', 'name'],
                                multiprocess_mode='livesum')


def func_metrics(name=None):
    """works within routes"""

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if inspect.isfunction(name):
                func_name = name(*args, **kwargs)
            else:
                func_name = name or func.__qualname__

            from ab import app
            app_name = app.config['APP_NAME']

            # count all
            c_func_calls.labels(app=app_name, name=func_name).inc()
            # count errors
            with c_func_errors.labels(app=app_name, name=func_name).count_exceptions():
                # accumulate inprogress
                with g_inprogress_func_calls.labels(app=app_name, name=func_name).track_inprogress():
                    # calculate time
                    with h_func_call_duration_seconds.labels(app=app_name, name=func_name).time():
                        return func(*args, **kwargs)

        return inner

    return wrapper


h_general_duration_seconds = Histogram("general_duration_seconds", "", labelnames=['app', 'name'])


def time_metrics(name):
    """general time metrics"""

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            from ab import app
            app_name = app.config['APP_NAME']

            with h_general_duration_seconds.labels(app=app_name, name=name).time():
                return func(*args, **kwargs)

        return inner

    return wrapper
