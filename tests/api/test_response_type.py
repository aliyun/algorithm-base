

def test_response_type(client):
    resp = client.post_data('/api/algorithm/response_type')
    assert 6 == len(resp["data"]["result"])
    assert resp['code'] == 0
