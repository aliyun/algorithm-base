# coding: utf-8


def test_none_compress(client):
    url = '/api/algorithm/none_compress'
    resp = client.post_data(url)
    assert resp['code'] == 0


def test_compress(client):
    url = '/api/algorithm/compress.zip'
    resp = client.get(url)


