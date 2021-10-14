from ab.utils import eureka


token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2luZm8iOnsiY29kZSI6InN1Y2Nlc3MiLCJuaWNrTmFtZSI6ImdzMSIsImFwcE5hbWUiOiJfX2Jhc2VfXyIsInRlbmFudElkIjoiNjUwIiwidGVuYW50Q29kZSI6ImdzIiwidXNlck5hbWUiOiJnczEiLCJ1c2VySWQiOiIxMDMxOCJ9LCJ1c2VyX25hbWUiOiJnczEiLCJzY29wZSI6WyJhcHAiXSwiZXhwIjoxNTY3OTc2MTY0LCJhdXRob3JpdGllcyI6WyJUTlRfQURNSU4iXSwianRpIjoiZTEzMWY3MGItM2Q2Ni00NWYxLWFkNTYtNGRhZDI4OTg2ZTFkIiwiY2xpZW50X2lkIjoiV2lzZG9tVGF4In0.jBp9CFn8wC00N-glBmkNkH0ZbIUM3gLjJnwieMYCBnU'


def test_upload_pickle(client):
    eureka_client = eureka.get_instance()
    resp = eureka_client.do_service('modelstore', "/api/models", method='post',
                                    headers={'Authorization': 'Bearer ' + token},
                                    data={'name': '', 'remark': '', 'type': '', 'algo_type': 0, 'algo_name': '',
                                          'workspace_code': 10000506, 'table_args': '{}', 'args': '{}', 'result': '{}'},
                                    files={'file': open('/Users/cx/Downloads/2769661_di-suite.cn_nginx.zip', mode='rb')},
                                    )
    print(resp)
