from ab.utils.prometheus import http_metrics
from flask import request

from ab import app, jsonify

from ab.services import data_source as dss
from ab.utils import data_source as dsu
from ab.plugins import cache


@app.route('/api/data_source/<int:data_source_id>/table/<string:table_name>/cache', methods=['DELETE'])
@http_metrics()  # must be decorated by @app.route
def delete_table_cache(data_source_id, table_name):
    ds_config = dss.get_data_source_by_id(data_source_id)
    ds = dsu.CachedDataSource(ds_config, table_name)
    ds.delete_table_cache()
    return jsonify({"code": 0, "data": 'success'})
