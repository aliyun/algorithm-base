"""
special utils for prometheus
refer to: https://github.com/prometheus/client_python#multiprocess-mode-gunicorn
"""
import multiprocessing
import os
import tempfile
import sys


# must precedent all imports of prometheus_client
if 'prometheus_client' in sys.modules.keys():
    raise ImportError('must set prometheus_multiproc_dir before import prometheus client')
# use a new temp dir each time
os.environ['prometheus_multiproc_dir'] = tempfile.mkdtemp()


from prometheus_client import multiprocess, Counter
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, Gauge


def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)


def app(environ, start_response):
    """
    prometheus app for gunicorn multi-process mode
    """
    from ab.utils.prometheus import c_http_requests
    from ab import app
    app_name = app.config['APP_NAME']

    c_http_requests.labels(app=app_name, method='GET', code=200, url='/metrics').inc()

    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    status = '200 OK'
    response_headers = [
        ('Content-type', CONTENT_TYPE_LATEST),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])

