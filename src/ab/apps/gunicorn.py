from gunicorn.app.wsgiapp import WSGIApplication
import gc

from ab import app, prometheus_app
from ab.apps import prometheus
from ab.utils import logger
from ab.plugins import prob
from ab.plugins.spring import eureka
from ab.decorate import warmup, when_ready_hooks, on_starting_hooks
from ab.plugins.config.config_reader import read_local_config_files


def post_fork(server, worker):
    eureka.post_fork(server, worker)


def post_worker_init(worker):
    warmup.do_warmup(worker)


def child_exit(server, worker):
    prometheus.child_exit(server, worker)


def when_ready(server):
    """
    in order to share the memory between workers.
    freeze the gc before fork, it can avoid the copy on write operation when preload set to True.
    :param server:
    :return:
    """
    when_ready_hooks.do_callback(server)

    gc.freeze()


def on_starting(server):
    on_starting_hooks.do_callback(server)


class GunicornApp(WSGIApplication):
    """
    gunicorn as the default, but changeable, server
    1. load all configs, then pass it to gunicorn app and flask app
    2. check app_uri
    """
    default_hooks = {
        'post_fork': post_fork,
        'child_exit': child_exit,
        'when_ready': when_ready,
        'post_worker_init': post_worker_init,
        'on_starting': on_starting,
    }

    # @override
    def load_wsgiapp(self):
        """
        init according to configs
        """
        app.load_submodules()

        user_app = super(GunicornApp, self).load_wsgiapp()
        if user_app is not prometheus_app:
            logger.warning('app_uri got modified, please make sure it is based on ab.app')
        return user_app

    # @override
    def init(self, parser, opts, args) -> dict:
        """
        read local config, set flask app config and return gunicorn config

        WSGIApplication __init__ -> do_load_config -> load_config -> init
        """
        # config = ap & flask config + gunicorn config
        config = read_local_config_files(args[0] if args else None)

        # overwrite WSGIApplication.init, allow config app_url
        self.app_uri = config.get('app_uri', 'ab:prometheus_app')
        self.cfg.set("default_proc_name", self.app_uri)

        # inject configs into the default ab flask app
        # do not load modules at this stage. hard to debug
        app.load_config(config)

        # do initialize before fork
        prob.init(config)

        gunicorn_config = self.convert_to_gunicorn_config(config)
        return gunicorn_config

    def convert_to_gunicorn_config(self, config):
        # ab & flask config to gunicorn config
        new_bind = config['HOST'] + ':' + str(config['PORT'])
        if 'bind' in config and config['bind'] != new_bind:
            logger.warning('overwrite gunicorn bind address "{bind}" by "{new_bind}"'.format(
                bind=config['bind'], new_bind=new_bind))
        config['bind'] = new_bind

        if 'proc_name' in config and config['proc_name'] != config['APP_NAME']:
            logger.warning('overwrite gunicorn proc_name "{proc_name}" by "{app_name}"'.format(
                proc_name=config['proc_name'], app_name=config['APP_NAME']
            ))
        config['proc_name'] = config['APP_NAME']

        if 'LOG_LEVEL' in config:
            if 'loglevel' in config and config['loglevel'] != config['LOG_LEVEL']:
                logger.warning('overwrite gunicorn loglevel "{loglevel}" by "{new_loglevel}"'.format(
                    loglevel=config['loglevel'], new_loglevel=config['LOG_LEVEL']
                ))
            config['loglevel'] = config['LOG_LEVEL']

        if 'debug' in config and config['debug'] != config['DEBUG']:
            logger.warning('overwrite gunicorn debug "{debug}" by "{new_debug}"'.format(
                debug=config['debug'], new_debug=config['DEBUG']
            ))
        config['debug'] = config['DEBUG']

        for hook_name, default_hook in self.default_hooks.items():
            if hook_name not in config:
                # default hook not set, use the default one
                config[hook_name] = default_hook
                continue

            # # combine default and user-defined hook
            def combined_hook(**kwargs):
                default_hook(**kwargs)
                config[hook_name](**kwargs)

            config[hook_name] = combined_hook

        # return gunicorn config kv
        return {k: v for k, v in config.items() if k in self.cfg.settings}


def run():
    """
    The ``gunicorn`` command line runner for launching Gunicorn with
    generic WSGI applications.
    """
    gapp = GunicornApp("%(prog)s [config1,config2...]")
    gapp.run()


if __name__ == "__main__":
    run()
