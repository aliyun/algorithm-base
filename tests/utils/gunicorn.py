import sys
import time
from multiprocessing import Process

import requests

from ab import app
from ab.apps.gunicorn import GunicornApp


def run_gunicorn(argv=[]):
    sys.argv = argv
    app = GunicornApp("%(prog)s [config1,config2...]")
    app.run()


def test_default_config(client):
    p = Process(target=run_gunicorn, daemon=True)
    p.start()  # fork
    time.sleep(100)

    resp = requests.get('http://localhost:{port}/'.format(port=app.config.PORT))
    assert resp.status_code == 200
    p.kill()


def test_env_config(client):
    p = Process(target=run_gunicorn, args=(['dev',],), daemon=True)
    p.start()  # fork

    resp = requests.get('http://localhost:{port}/'.format(port=app.config.PORT))
    assert resp.status_code == 200
    p.kill()
