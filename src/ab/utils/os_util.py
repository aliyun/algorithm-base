import os


def is_main_process():
    """
    linux only
    """
    pid = os.getpid()
    pgid = os.getpgid(pid)
    return pid == pgid


def resource_file_path(resource_file_path):
    pythonpath = os.environ['PYTHONPATH']

    for dir in pythonpath.split(os.pathsep):
        resource_path = os.path.join(dir, resource_file_path)
        if os.path.exists(resource_path):
            return resource_path
