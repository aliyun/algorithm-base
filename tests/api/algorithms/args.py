from ab.utils import logger
from ab.utils.algorithm import algorithm


@algorithm('args')
def get_data(task_id, data_source_id=None, table_name=None, data=None, table_info=None, recorder=None, cache_client=None,
             dfs_client=None, eureka_client=None, qs_arg=None, f1=None, single_form_arg: int = None,
             couple_form_args: int = None, the_file=None):
    logger.info('get task_id:', task_id)
    return {'task_id': task_id, 'data_source_id': data_source_id, 'table_name': table_name, 'data': data,
            'table_info': table_info, 'recorder': str(recorder), 'cache_client': str(cache_client),
            'dfs_client': str(dfs_client), 'eureka_client': str(eureka_client), 'spark': None, # spark init is slow, disable it here
            'qs_arg': qs_arg, 'f1': f1, 'single_form_arg': single_form_arg, 'couple_form_args': couple_form_args,
            'the_file_context': the_file.read().decode('utf-8') if the_file else None,
            'the_filename': the_file.filename if the_file else None
            }


@algorithm()
def fixture_overwrite(f2=None, f3=None):
    return f2, f3
