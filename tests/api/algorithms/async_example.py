import time
import pandas as pd

from ab.utils import logger
from ab.utils.algorithm import algorithm

# 算法执行前算法状态已经初始化
# 此时调用task_status接口会返回{'code': 0, 'status': None, 'data': None}。0代表已经初始化，但还没开始执行
@algorithm(name='async_example')
def main(data: pd.DataFrame, table_info, recorder, name='test', print_data=True):
    '''
    输入：
        data:
        table_info:
        recorder: 异步算法用于更新算法状态的handler。同步算法也会获得一个dummy recorder，但不执行任何工作
    '''
    # 如果异步任务太多，main函数可能会排队等待执行
    # 如果想立即让前端知道算法已经开始执行，则记得在算法开始立即update一下
    # update_status参数必须是可以序列化的对象
    recorder.update_status('begin')
    # 此时调用task_status接口会返回{'code': 1, 'status': 'begin', 'data': None}。1代表正在执行

    # do some work...
    if print_data:
        # logger.debug(len(set(data['gender'])))
        logger.debug(">>>>>>>>>>>>>>")
        logger.debug(data)
    # logger.debug(table_info)
    # logger.debug(name)
    time.sleep(1)
    recorder.update_status({'stage': 'stage1'})
    # 此时调用task_status接口会返回{'code': 1, 'status': {'stage': 'stage1'}, 'data': None}。1代表正在执行

    # i = 1 / 0
    # 如果算法运行中产生异常，main函数会立即退出，且task_status接口会返回{'code': -1, 'status': 异常栈string, 'data': None}。-1代表异常

    # do more works
    time.sleep(1)
    recorder.update_status('stage2')

    time.sleep(1)
    return ['hello', 'world']  # 返回值必须是一个可以序列化的对象
    # 从main函数返回后框架会更新算法运行结果
    # 此时调用task_status接口会返回 {
    #     'code': 2,  # 2代表运行结束
    #     'status': 'stage2',
    #     'data': {
    #         'result': ['hello', 'world'],
    #         "sample_count": 50, # 采样条数
    #         "sample_rate": 100  # 采样率
    #     }
    # }

    # 算法运行结果默认缓存一天，超时后再调用task_status接口会返回{'code': -1, 'status': f'{task_id} not found', 'data': None}
