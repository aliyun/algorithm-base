from collections import OrderedDict
from ab.utils.prometheus import http_metrics
from ab.plugins.db.db_master import get_mapper
from flask import request
from ab import app, jsonify


mapper = get_mapper('_task')
list_columns = 'task_id,app_name,algorithm_name,code,args,status,spark_app_id,gmt_create,gmt_modified'


@app.route('/api/task', methods=['GET'])
@http_metrics()  # must be decorated by @app.route
def get_tasks():
    args = request.args.to_dict()
    page = int(args.pop('page', 1))
    size = int(args.pop('size', 10))

    # make app_name the first where condition
    args = OrderedDict(args)
    args['app_name'] = app.config.APP_NAME
    args.move_to_end('app_name', last=False)

    rows = mapper.select_page(fields=list_columns, conditions=args, order_by='id DESC', page=page, size=size)
    count = mapper.count(conditions=args)
    return jsonify({"code": 0, "data": rows, "count": count})


@app.route('/api/task/<string:task_id>', methods=['GET'])
@http_metrics()  # must be decorated by @app.route
def get_task_by_id(task_id):
    row = mapper.select_one_by_id(task_id)
    return jsonify(row)
