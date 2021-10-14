

def test_user(client, login_info):
    input = {}
    resp = client.post_data('/api/algorithm/user', input)
    assert resp['code'] == 0
    if login_info:
        assert resp['data']['result']
    else:
        assert not resp['data']['result']
