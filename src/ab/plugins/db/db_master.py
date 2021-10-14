"""
expose db as route
"""
from functools import partial, update_wrapper

from ab.utils.prometheus import http_metrics, time_metrics
from flask import request

from ab.plugins.db.dao import Mapper


mappers = {}


def get_mapper(key) -> Mapper:
    return mappers[key]


@time_metrics('dbm')
def init_dbm(config):
    """
    dynamically add route for db tables
    """
    if not config.DBM:
        return

    from ab import app
    for table in config.DBM:
        # prepare mapper
        json_columns = table.get('json_columns')
        if isinstance(json_columns, str):
            table['json_columns'] = json_columns.split(',')
        mapper = Mapper(**table)
        key = table.get('key') or table['table_name']
        mappers[key] = mapper

        # default values for dbm properties
        list_columns = table.get('list_columns', '*')
        if isinstance(list_columns, str) and list_columns != '*':
            list_columns = list_columns.split(',')
        detail_columns = table.get('detail_columns', '*')
        if isinstance(detail_columns, str) and detail_columns != '*':
            detail_columns = detail_columns.split(',')
        default_page_size = table.get('default_page_size', 10)
        max_page_size = table.get('max_page_size', 50)
        operations = table.get('operations', 'CRUD')

        # bind url
        if 'C' in operations:
            app.add_url_rule('/api/table/{key}'.format(key=key),
                 'add_' + key,
                 update_wrapper(partial(add, mapper), add),
                 methods=['POST'])
        if 'R' in operations:
            app.add_url_rule('/api/table/{key}'.format(key=key),
                 'list_page_' + key,
                 update_wrapper(partial(list_page, mapper, list_columns, default_page_size, max_page_size), list_page),
                 methods=['GET'])
            app.add_url_rule('/api/table/{key}/<int:id>'.format(key=key),
                 'get_one_by_id_' + key,
                 update_wrapper(partial(get_one_by_id, mapper, fields=detail_columns), get_one_by_id),
                 methods=['GET'])
        if 'U' in operations:
            app.add_url_rule('/api/table/{key}/<int:id>'.format(key=key),
                 'update_one_by_id_' + key,
                 update_wrapper(partial(update_one_by_id, mapper), update_one_by_id),
                 methods=['PUT'])
        if 'D' in operations:
            app.add_url_rule('/api/table/{key}/<int:id>'.format(key=key),
                             'delete_one_by_id_' + key,
                             update_wrapper(partial(delete_one_by_id, mapper), delete_one_by_id),
                             methods=['DELETE'])


@http_metrics()
def list_page(mapper, list_columns, default_page_size, max_page_size):
    # TODO args order
    args = request.args.to_dict()
    page = int(args.pop('page', 1))
    size = int(args.pop('size', default_page_size))
    assert size <= max_page_size, 'page size must not exceed {max_page_size}'.format(max_page_size=max_page_size)
    order_by = args.pop('order_by', None)
    rows = mapper.select_page(fields=list_columns, conditions=args, order_by=order_by, page=page, size=size)
    count = mapper.count(conditions=args)
    from ab import jsonify
    return jsonify({"code": 0, "data": rows, "count": count})


@http_metrics()
def get_one_by_id(mapper, id, fields='*'):
    row = mapper.select_one_by_id(id, fields=fields)
    from ab import jsonify
    return jsonify({"code": 0, "data": row})


@http_metrics()
def add(mapper):
    row = request.get_json()
    row_id = mapper.insert(row)
    from ab import jsonify
    return jsonify({"code": 0, "data": row_id})


@http_metrics()
def update_one_by_id(mapper, id):
    row = request.get_json()
    ret = mapper.update_one_by_id(id, row)
    from ab import jsonify
    return jsonify({"code": 0, "data": ret})


@http_metrics()
def delete_one_by_id(mapper, id):
    ret = mapper.delete_one_by_id(id)
    from ab import jsonify
    return jsonify({"code": 0, "data": ret})
