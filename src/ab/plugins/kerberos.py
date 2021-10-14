import sys
import subprocess
from threading import Thread, Event

from ab.utils import logger

kerberos_inited = False

from threading import Timer


class LiveTimer(Timer):

    def run(self):
        while True:
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
            else:
                break


def init_kerberos(config):
    if not config.KERBEROS:
        logger.info('no config.KERBEROS found, kerberos uninitialized')
        return
    kinit(**config.KERBEROS)
    global kerberos_inited
    kerberos_inited = True


def _inner_kinit(cmd, input):
    logger.info('kerberos:', cmd)
    # check=True: raise CalledProcessError if rc != 0
    # alway returns 0 on success
    for i in range(3):
        try:
            return subprocess.run(cmd, input=input, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  check=True).returncode
        except Exception as e:
            if i == 2:
                raise


def kinit(principal, keytab: str = None, password: str = None, refresh_interval_in_seconds=3600):
    """
    always return 0
    raise CalledProcessError on error
    """
    assert (keytab and not password) or (password and not keytab), 'kinit need either keytab or password'

    cmd = ['kinit', principal]
    input = password.encode() if password else None
    if keytab:
        cmd.extend(['-kt', keytab])

    timer = LiveTimer(refresh_interval_in_seconds, _inner_kinit, kwargs={'cmd': cmd, 'input': input})
    timer.daemon = True
    timer.start()

    return _inner_kinit(cmd, input)


