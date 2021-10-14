import random
import subprocess

import redis

import pytest

from ab.tests.pytest_plugin import JsonFlaskClient

from ab.utils import logger

from ab.apps.flask import FlaskApp


from tests import config, min_config


@pytest.fixture(scope="session", autouse=True)
def init():
    subprocess.run(['kdestroy', '-A'])

    # randomly clear redis cache before tests startup
    if random.random() > 0.5:
        logger.info('redis not clear')
        return
    logger.info('randomly clear redis for robustness')
    conn = redis.StrictRedis(**config.REDIS)
    conn.flushall()


def login_info(request):
    return {'username': 'your-username', 'password': 'your-password'}


# def pytest_sessionfinish(session, exitstatus):
#     # logger.info('whole test run finishes, clear')
#     pass


@pytest.fixture(scope="session")
def config_root():
    return 'tests'


@pytest.fixture(scope="session")
def min_config_client():
    # init min app manually
    min_app = FlaskApp(__name__)
    min_app.load_config(min_config)
    min_app.load_submodules()
    from ab.controllers.algorithm import run_algorithm_backend
    min_app.add_url_rule('/api/algorithm', methods=['GET', 'POST'], view_func=run_algorithm_backend)
    # identify in test mode
    # change client impl
    min_app.test_client_class = JsonFlaskClient
    client = min_app.test_client()

    yield client
