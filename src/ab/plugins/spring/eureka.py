import sys
import atexit
import urllib
import socket
import requests
import py_eureka_client.eureka_client as eureka_client
from flask import has_request_context

from ab.utils import logger
from ab.utils.prometheus import func_metrics, time_metrics

registry_client = None
discovery_client = None


@time_metrics('eureka')
def init_eureka_registry_client(config):
    """
    register self as micro service in gunicorn master process
    """
    global registry_client

    if not config.EUREKA_SERVER:
        logger.info('eureka not configured, ignore')
        return

    if config.REGISTER_AT_EUREKA:
        # init registry client
        app_name = config.APP_NAME
        # The flowing code will register your server to eureka server and also start to send heartbeat every 30 seconds
        registry_client = eureka_client.init_registry_client(eureka_server=config.EUREKA_SERVER,
                                                             app_name=app_name,
                                                             instance_port=int(config.PORT),
                                                             instance_host=config.INSTANCE_HOST,
                                                             instance_ip=config.INSTANCE_IP,
                                                             renewal_interval_in_secs=5,
                                                             duration_in_secs=10)
        # eureka_client already registered
        logger.debug('main process register at eureka as \033[33m{app_name}\033[0m: {registry_client}\n'.format(
            app_name=app_name, registry_client=registry_client))


def init_eureka_discovery_client(config=None):
    """
    init discovery client, used in forked worker processes or pytest main process
    """
    global discovery_client

    from ab import app
    config = config or app.config

    if not config.EUREKA_SERVER:
        return
    discovery_client = EurekaDiscoveryClient(config.EUREKA_SERVER)


def post_fork(server, worker):
    init_eureka_discovery_client()


class EurekaDiscoveryClient:
    """
    eureka client for invoking other services
    """
    def __init__(self, eureka_server):
        self.eureka_server = eureka_server
        try:
            self.discovery_client = eureka_client.init_discovery_client(eureka_server=eureka_server, renewal_interval_in_secs=10)
        except (socket.timeout, urllib.error.URLError) as e:
            logger.exception(e)
            logger.error("can't connect to eureka server, please check your network and config.EUREKA_SERVER")
            sys.exit(-1)
        atexit.register(self.stop)

    @staticmethod
    def get_auth_token():
        """
        :return: auth token in request header
        """
        if not has_request_context():
            return None
        from flask import request
        return request.headers.get('Authorization') or request.args.get('access_token')

    @func_metrics('eureka')
    def do_service(self, app_name, service, return_type="json",
                   method="get", headers: dict=None,
                   data=None, json=None, files: dict=None,
                   prefer_ip=True, prefer_https=False,
                   timeout=None,
                   ):
        """
        integrate eureka_client and requests

        :param app_name:
        :param service:
        :param return_type:
        :param method: method for the new :class:`Request` object.
        :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
        :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
            ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
            or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
            defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
            to add for the file.
        :param prefer_ip:
        :param prefer_https:
        :param timeout: (optional) How many seconds to wait for the server to send data
            before giving up, as a float, or a :ref:`(connect timeout, read
            timeout) <timeouts>` tuple.
        """
        # check method
        method = method.lower()
        if files:
            assert method == 'post'

        # fill headers
        headers = headers or {}
        if 'Authorization' not in headers:
            auth_header = self.get_auth_token()
            if auth_header:
                headers['Authorization'] = auth_header
        if not headers:
            logger.debug('empty eureka request headers')

        # copy from eureka_client and patch walker func
        def walk_using_requests(url):
            """
            data or files, if present, will overwrite json
            data and files could co-exist
            See :func:`requests.models.PreparedRequest#prepare_body`
            """
            logger.info('requesting url: {url}'.format(url=url))
            resp = requests.request(method, url, headers=headers, files=files, json=json, data=data, timeout=timeout)
            if return_type == 'json':
                return resp.json(encoding='utf8')
            elif return_type == 'raw':
                return resp
            else:
                return resp.text

        return self.discovery_client.walk_nodes(app_name, service, prefer_ip, prefer_https, walk_using_requests)

    @property
    def applications(self):
        return self.discovery_client.applications

    def stop(self):
        return self.discovery_client.stop()


def get_instance() -> EurekaDiscoveryClient:
    return discovery_client


def pretty_print_request(req: requests.Request):
    """
    usage example:
        req = requests.Request('POST','http://stackoverflow.com',headers={'X-Custom':'Test'},data='a=1&b=2')
        pretty_print_request(req)
    """
    req = req.prepare()
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))
