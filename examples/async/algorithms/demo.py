import time
from ab.utils.algorithm import algorithm
from ab.utils.recorder import DummyTaskRecorder, TaskRecorder


# 会自动暴露为/api/algorithms/async_work接口
@algorithm()
def async_work(run_seconds, recorder=DummyTaskRecorder):

    # 执行过程中可以调用update_status更新任务状态，让code变为1，方便前端获取任务执行进度
    recorder.update_status(code=TaskRecorder.RUNNING, status={'progress': 0})

    # 模拟一个需要长时间执行的任务
    time.sleep(run_seconds)

    recorder.update_status(code=TaskRecorder.RUNNING, status={'progress': 99})

    return 'successfully sleep for {run_seconds} seconds'.format(run_seconds=run_seconds)
    # 执行完成后code会自动变为2，结果也塞到数据库里

