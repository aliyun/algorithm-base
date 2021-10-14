from ab.utils.fixture import fixture


@fixture()
def f1(request, kwargs):
    print(request, kwargs)
    return 'this is f1'


@fixture()
def f2(request, kwargs):
    return 'this is f2'


@fixture(overwrite=True)
def f3(request, kwargs):
    return 'this is f3'
