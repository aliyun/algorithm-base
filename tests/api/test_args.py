import io

from werkzeug.datastructures import MultiDict


def test_qs_args(client):
    input = {}
    resp = client.post_data('/api/data_source/10000506/table/e_annual_performance/algorithm/args?qs_arg=123', input)
    assert resp['code'] == 0
    assert resp['data']['result']['qs_arg'] == '123'


def test_only_file_upload_arg(client):
    input = {'the_file': (io.BytesIO(b'hello world'), 'filename.mp3')}
    resp = client.post_form('/api/data_source/10000506/table/e_annual_performance/algorithm/args?qs_arg=123',
                            data=input, content_type='multipart/form-data')
    assert resp['code'] == 0
    assert resp['data']['result']['the_file_context'] == 'hello world'
    assert resp['data']['result']['the_filename'] == 'filename.mp3'


def test_plain_form_args(client):
    input = MultiDict([('single_form_arg', 'single_dog'),
                       ('couple_form_args', 'male'),
                       ('couple_form_args', 'female'),
                       ])
    resp = client.post_form('/api/data_source/10000506/table/e_annual_performance/algorithm/args?qs_arg=123',
                            data=input, content_type='multipart/form-data')
    assert resp['code'] == 0
    assert resp['data']['result']['qs_arg'] == '123'
    assert resp['data']['result']['single_form_arg'] == 'single_dog'
    assert resp['data']['result']['couple_form_args'] == ['male', 'female']


def test_all_args(client):
    input = MultiDict([('single_form_arg', 'single_dog'),
                       ('couple_form_args', 'male'),
                       ('couple_form_args', 'female'),
                       ('the_file', (io.BytesIO(b'hello world'), 'filename.mp3'))
                       ])
    resp = client.post_form('/api/data_source/10000506/table/e_annual_performance/algorithm/args?qs_arg=123',
                            data=input, content_type='multipart/form-data')
    assert resp['code'] == 0
    assert resp['data']['result']['qs_arg'] == '123'
    assert resp['data']['result']['single_form_arg'] == 'single_dog'
    assert resp['data']['result']['couple_form_args'] == ['male', 'female']
    assert resp['data']['result']['the_file_context'] == 'hello world'
    assert resp['data']['result']['the_filename'] == 'filename.mp3'

