from ab.tests.pytest_plugin import JsonFlaskClient


def test_static(client: JsonFlaskClient):
    resp = client.get('/tests/static/', follow_redirects=True)
    assert resp.status_code == 200
    assert resp.mimetype == 'text/html'
    assert resp.get_data(as_text=True) == '<h1>Hello World!</h1>'

    resp = client.get('/tests/static/index.html')
    assert resp.status_code == 200
    assert resp.mimetype == 'text/html'
    assert resp.get_data(as_text=True) == '<h1>Hello World!</h1>'

    resp = client.get('/tests/static/c.css')
    assert resp.status_code == 200
    assert resp.mimetype == 'text/css'
    assert resp.get_data(as_text=True) == 'c'

    resp = client.get('/tests/static/j.js')
    assert resp.status_code == 200
    assert resp.mimetype == 'application/javascript'
    assert resp.get_data(as_text=True) == 'j'
