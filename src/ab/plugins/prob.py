import subprocess
import sys
import time
import threading
import requests
import signal

from ab.utils import logger

restart = False


def quit(signal_num, frame):
    logger.info("you stop the threading")
    sys.exit()


def init(config):
    if config.ENABLE_LIVENESS_PROB:
        logger.info("enable liveness prob: True")
        start_liveness_prob(config)
    else:
        logger.info("enable liveness prob: False")



def liveness_prob(config):
    liveness_start_counter = 0
    liveness_period_counter = 0
    liveness_error_counter = 0

    while True:
        if liveness_start_counter >= config.LIVENESS_PROB["initialDelaySeconds"]:
            if liveness_period_counter % config.LIVENESS_PROB["periodSeconds"] == 0:
                try:
                    url = "http://{}:{}".format("127.0.0.1", config.PORT)
                    r = requests.get(url, timeout=config.LIVENESS_PROB["timeoutSeconds"])
                    liveness_error_counter = 0
                except Exception as e:
                    logger.error("error in liveness prob:", e)
                    liveness_error_counter = liveness_error_counter + 1

        liveness_start_counter = liveness_start_counter + 1
        liveness_period_counter = liveness_period_counter + 1

        if liveness_error_counter >= config.LIVENESS_PROB["failureThreshold"]:
            restart_handler()
            break
        time.sleep(1)


def start_liveness_prob(config):
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    t = threading.Thread(target=liveness_prob, args=(config,))
    t.setDaemon(True)
    t.start()


def restart_handler():
    global restart
    if not restart:
        restart = True
        logger.error("!!!!! going to RESTART ###### ")

        get_pid_command = "ps aux | grep master | grep gunicorn | sort | awk '{print $2}' | head -1"
        pid = subprocess.run(get_pid_command, shell=True, stdout=subprocess.PIPE, encoding="utf-8").stdout
        pid = pid.strip()

        logger.error("gunicorn master pid is {}".format(pid))
        command = "kill {}".format(pid)
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, encoding="utf-8").stdout
        logger.error(ret)


def in_container():
    command = "uname"
    ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, encoding="utf-8").stdout
    return True if ret.lower().strip() == "linux" else False

# todo: one idea is to start the health check outside the container
# from ab.utils.config_reader import read_local_config_files
# def main(args):
#     """
#     start the liveness prob outside the web server
#     :param args:
#     :return:
#     """
#     config = read_local_config_files(args[0] if args else None)
#     init(config)
# if __name__ == '__main__':
#     main(args=sys.argv[1:])

