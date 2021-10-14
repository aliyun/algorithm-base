from werkzeug.middleware.dispatcher import DispatcherMiddleware

from ab.apps import prometheus
from ab.apps.flask import FlaskApp, jsonify
from flask import request


app = FlaskApp(__name__)

# Add prometheus wsgi middleware to route /metrics requests
prometheus_app = DispatcherMiddleware(app, {
    '/metrics': prometheus.app,
    '/actuator/prometheus': prometheus.app,
    # aone ignores default '/auctuator' prefix
    '/prometheus': prometheus.app,
})
