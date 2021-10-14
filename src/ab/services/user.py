import base64
import json

from werkzeug.exceptions import Unauthorized

from ab import app

from ab.utils import logger
from ab.plugins.spring import eureka


def _login(username, password):
    """
    only for test
    :return the access token
    """
    try:
        logger.info('login as user {username}'.format(username=username))
        eureka_client = eureka.get_instance()

        login_resp = eureka_client.do_service('GOVBRAIN-AUTHCENTER', '/commonuser/login', method='post',
                                        json={'username': username, 'password': password})
        ticket = login_resp['data']['ticket']
        if app.config.TESTING:
            logger.debug('ticket for user', username, 'is:', ticket)

        resp = eureka_client.do_service('GOVBRAIN-AUTHCENTER', '/commonuser/ticket_login?ticket={ticket}'.format(ticket=ticket),
                                        method='get')
        if app.config.TESTING:
            logger.debug('access_token for user', username, 'is:', resp['data']['access_token'])
        return resp['data']['access_token']
    except Exception as e:
        logger.error('login fail, please check username/password')
        raise


def get_current_user(s: str=None, required=True):
    """
    get current user by request auth header
    :param s:
    :return:
        {'code': 'SUCCESS', 'nickName': 'gs1', 'appName': '__base__',
        'tenantId': '650', 'tenantCode': 'gs', 'userName': 'gs1', 'userId': '10318'}
    """
    eureka_client = eureka.get_instance()
    s = s or eureka_client.get_auth_token()
    if not s:
        if required:
            raise Unauthorized('login required')
        else:
            return None
    # format not checked
    b64encoded = s[7:].split('.')[1]
    decoded = base64.urlsafe_b64decode(b64encoded + '===').decode('utf-8')
    return json.loads(decoded)['user_info']
