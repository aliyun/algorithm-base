from ab.utils import logger


def test(min_config_client):
    input = {
        "algorithm": "args"
    }
    resp = min_config_client.post_data('/api/algorithm', input)
    assert resp['code'] == 0, resp
    logger.info('resp = ', resp)
