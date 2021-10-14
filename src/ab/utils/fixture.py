import inspect
import pkgutil

from ab.utils.exceptions import AlgorithmException


fixtures = {}


class Fixture:
    """
    stateless class for fixture abstraction
    """
    @classmethod
    def get_instance(cls, name: str):
        try:
            return fixtures[name]
        except KeyError as e:
            raise AlgorithmException(-1, 'fixture {name} not found'.format(name=name)) from e

    @staticmethod
    def process_signature(func):
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        defaults_map = {key: value.default for key, value in sig.parameters.items() if value.default != sig.empty}
        return sig, params, defaults_map

    def __init__(self, name, func, overwrite=False):
        """
        :param name:
        :param func:
        :param overwrite: whether overwrite existing kwarg
        """
        self.name = name
        self.main = func
        self.overwrite = overwrite
        self.sig, self.params, self.defaults_map = Fixture.process_signature(func)

    def run(self, request, kwargs):
        return self.main(request, kwargs)


def fixture(name=None, overwrite=False):
    """
    register func as fixture entry
    same as Java Spring @Service
    :param name: name of the fixture. use func.__name__ if name is None
    """
    def register_func(func):
        register_fixture(name, func, overwrite)
        return func

    return register_func


def register_fixture(name: str, func, overwrite: bool):

    name = name or func.__name__
    # TODO check duplication
    fixtures[name] = Fixture(name, func, overwrite)


def register_all_fixtures(config):
    """
    auto-import all modules under fixtures for registry
    """
    fixture_dir = config.get('FIXTURE_DIR', 'fixtures')
    for _, modname, _ in pkgutil.iter_modules([fixture_dir, ]):
        __import__('{fixture_dir}.{modname}'.format(fixture_dir=fixture_dir.replace("/", "."), modname=modname))

    from ab.utils import logger
    logger.debug('fixtures:', fixtures)
