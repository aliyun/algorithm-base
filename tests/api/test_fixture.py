import pytest

from ab.utils import logger
from ab.utils.exceptions import AlgorithmException


def test_overwrite_fail(client):
    """f2 overwrite=False"""
    input = {'args': {'f2': 123}}
    with pytest.raises(AlgorithmException):
        resp = client.post_data('/api/algorithm/fixture_overwrite', input)


def test_overwrite_success(client):
    """f3 overwrite=True"""
    input = {'args': {'f3': 123}}
    resp = client.post_data('/api/algorithm/fixture_overwrite', input)
    assert resp['code'] == 0
    assert resp['data']['result'] == ['this is f2', 'this is f3']
