import sys

from ab.utils import logger
from ab.plugins.spring import eureka
from ab.utils.exceptions import RemoteAPIException


def check_and_return(resp):
    """
    check code == 0 and return data. otherwise raise exception
    """
    if resp['code'] != 0:
        raise RemoteAPIException(-2, resp['data'])
    return resp['data']


def get_data_source_app():
    """
    backward compatibility
    :return:  'DATASOURCE' < 'DATASOURCE_V2' < 'DATASOURCE-V2'
    """
    eureka_client = eureka.get_instance()
    # TODO eureka_client should provide `in` operator
    if eureka_client.applications.get_application('DATASOURCE-V2').instances:
        return 'DATASOURCE-V2'
    if eureka_client.applications.get_application('DATASOURCE_V2').instances:
        return 'DATASOURCE_V2'
    if eureka_client.applications.get_application('DATASOURCE').instances:
        return 'DATASOURCE'
    logger.error('no data source service found, please check eureka config then restart')
    sys.exit(-1)


def get_data_sources():
    """
    get data source list
    """
    eureka_client = eureka.get_instance()
    data_source_app = get_data_source_app()
    resp = eureka_client.do_service(data_source_app, "/api/schema")
    return check_and_return(resp)


def get_data_source_by_id(data_source_id, headers=None):
    """
    get one data source config by id
    """
    eureka_client = eureka.get_instance()
    data_source_app = get_data_source_app()

    resp = eureka_client.do_service(data_source_app,
                                    '/api/dataSource/{data_source_id}'.format(data_source_id=data_source_id),
                                    headers=headers)
    data_source = check_and_return(resp)
    return data_source


def get_user_workspace_by_code(workspace_code: str):
    """
    :returns {
            'workspaceCode': 'test_cs5',
            'workspaceId': 10000590,
            'workspaceName': 'test_cs5KK'
            }
        None if not found
    """
    eureka_client = eureka.get_instance()
    data_source_app = get_data_source_app()

    resp = eureka_client.do_service(data_source_app,
                                    '/api/workspace/{workspace_code}'.format(workspace_code=workspace_code))
    return check_and_return(resp)
