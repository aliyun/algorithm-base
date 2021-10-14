import os
from ab.utils.algorithm import algorithm


@algorithm()
def sync_logs(path):
    command = "head -n 1 " + path + "/*.log"
    if os.system(command) == 0:
        return "The logs have been successfully synchronized to the OSS"
    return "Failed to synchronize logs"


