from ab.utils.prometheus import http_metrics

from ab import app
from ab import jsonify
from ab.services import data_source


@app.route('/api/data_source/<int:data_source_id>', methods=['GET'])
@http_metrics()  # must be decorated by @app.route
def get_data_source_by_id(data_source_id):
    ds = data_source.get_data_source_by_id(data_source_id)
    return jsonify({"code": 0, "data": ds})
