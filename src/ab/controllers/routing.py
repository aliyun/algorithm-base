from ab.utils import logger
from ab import jsonify
from ab import app
from ab.utils.exceptions import AlgorithmException
from ab.utils.algorithm import algorithms


@app.route('/routing', methods=['GET', 'POST'])
def routing():
    """
    :return: the table of `algorithm-name:service-name`
    """
    ret = dict()
    ret["service2algo"] = ["{}:{}".format(app.config["APP_NAME"], algo.name) for algo in algorithms.values()]
    ret["algo2service"] = ["{}:{}".format(algo.name, app.config["APP_NAME"]) for algo in algorithms.values()]
    return jsonify({'code': 0, 'data': ret})
