import pytest
from flask.testing import FlaskClient

from ab import app
from ab.utils import serializer, logger
from ab.services.user import _login
from ab.plugins.cache.redis import cache_plugin
from ab.plugins.config.config_reader import read_local_config_files


def pytest_addoption(parser):
    group = parser.getgroup("pyab_test", "test options for pyab")
    group._addoption(
        "-e",
        "--abc",
        "--ab-configs",
        dest="abc",
        default="",
        action="store",
        help="format: 'config1,config2...'",
    )
    group._addoption(
        "-u",
        "--user",
        "--ab-user",
        dest="user",
        default=None,
        action="store",
        help="format: 'username:password'",
    )


class JsonFlaskClient(FlaskClient):
    """
    wrap json get & post

    class: https://flask.palletsprojects.com/en/1.1.x/api/#flask.testing.FlaskClient
    func args: https://werkzeug.palletsprojects.com/en/1.0.x/test/#werkzeug.test.EnvironBuilder
    """

    def get_data(self, *args, **kwargs):
        return self.get(*args, **kwargs).json

    def post_data(self, url, data={}):
        return self.post(url, json=data).json

    post_json = post_data

    def post_form(self, *args, **kwargs):
        return self.post(*args, **kwargs).json

    def put_data(self, url, data):
        return self.put(url, data=serializer.dumps(data), content_type='application/json').json

    def delete_data(self, *args, **kwargs):
        return self.delete(*args, **kwargs).json


@pytest.fixture(scope="session")
def login_info(request):
    logger.warning('''
    ab v2.5开始增加登录功能，免去了有些环境需要登录才能访问的烦恼。
    默认使用匿名用户，和以前保持一致，无需做任何改动。
    修改登录用户方法参考文档的"开发测试用例"章节，可以直接搜索关键字"login_info"。
    di-suite同一个用户只能有一个在线，多人共用一个账号可能会被踢下线然后报错。
    ''')
    cli_user = request.config.option.user
    if cli_user is None:
        return None

    if not cli_user:
        return None
    username, password = cli_user.split(':')
    return {'username': username, 'password': password}


@pytest.fixture(scope="session")
def access_token_generator(login_info):
    # singleton access_token for pytest-xdist
    def generator():
        if not login_info:
            # disable login
            return None

        if not app.config.EUREKA_SERVER:
            return None

        cache_client = cache_plugin.get_cache_client()
        c = cache_client.bget_set_cache('test.user.{username}.access_token.bin'.format(username=login_info['username']),
                                        lambda: _login(**login_info), expire=app.config.CACHE_TIMEOUT)
        return c

    return generator


@pytest.fixture(scope="session")
def config_root():
    """where to search for config files"""
    return 'config'


@pytest.fixture(scope="session")
def client(request, config_root, access_token_generator):
    config = read_local_config_files(request.config.option.abc, root=config_root)
    app.load_config(config)
    app.load_submodules()

    # change client impl
    app.test_client_class = JsonFlaskClient

    test_client = app.test_client()
    token = access_token_generator()
    if token:
        test_client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + token
    yield test_client
