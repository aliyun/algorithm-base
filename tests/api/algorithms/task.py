# coding: utf-8


from ab.utils.algorithm import algorithm


@algorithm()
def sync():
    return "hello-sync-task"


@algorithm()
def async_unlimit():
    import time
    time.sleep(2)
    return "hello-async-unlimit-task"


@algorithm()
def async_pool():
    import time
    time.sleep(2)
    return "hello-async-pool-task"
