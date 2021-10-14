import re
import requests
from requests.auth import HTTPBasicAuth
# from rauth import OAuth2Service


class OAuth2Client:
    token_key_regex = re.compile(r'<Map><alg>(?P<alg>.*)</alg><value>(?P<token_key>.*)</value></Map>')

    def __init__(self, oauth_host, client_id, client_secret):
        self.oauth_host = oauth_host
        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def token_key(self):
        token_key_res = requests.get('{self.oauth_host}/oauth/token_key'.format(self=self),
                                     auth=HTTPBasicAuth(self.client_id, self.client_secret))
        token_key_xml = token_key_res.text
        m = self.token_key_regex.match(token_key_xml)
        if not m:
            raise ValueError('unknown token key format: {token_key_xml}'.format(token_key_xml=token_key_xml))
        alg = m.group('alg')
        if alg != 'HMACSHA256':
            raise ValueError('unknown token key alg: {alg}'.format(alg=alg))
        return m.group('token_key')
