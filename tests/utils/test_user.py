from ab import app

from ab.services.data_source import get_user_workspace_by_code
from ab.services.user import get_current_user


def test_get_current_user(client, login_info):
    # force context
    with client:
        client.get('/')
        user = get_current_user(required=False)
    if login_info:
        assert user
    else:
        assert not user


def test_user_workspace(client):
    with client:
        client.get('/')

        ret = get_user_workspace_by_code('workspace_code_that_should_not_exists')
        assert ret is None

        ret = get_user_workspace_by_code('test_cs5')
        del ret['workspaceName']
        assert ret == {'workspaceCode': 'test_cs5', 'workspaceId': 10000590}

