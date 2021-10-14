#! python3
# encoding: utf8

from flask import current_app

from ab.task.task import Task
from ab.utils import logger, serializer


def run_algorithm(request):
    if isinstance(request, str):
        request = serializer.loads(request, encoding='utf8')

    sig = ', '.join(['{k}={v}'.format(k=k, v=v) for k, v in request['args'].items()]) if request.get('args') else ''
    logger.debug('run algorithm {algorithm}({sig}), sampler={sampler}'.format(
        algorithm=request['algorithm'], sig=sig, sampler=request.get('sampler')))

    task = Task.get_instance(request)
    result = task.run()

    if current_app.config.PRINT_RESULT:
        logger.debug(result)

    return result

