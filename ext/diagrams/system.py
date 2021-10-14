from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.analytics import Spark
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Gunicorn
from diagrams.programming.framework import Flask
from diagrams.onprem.aggregator import Fluentd
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Nginx
from diagrams.onprem.database import Mysql
from diagrams.onprem.analytics import Hive
from diagrams.onprem.inmemory import Redis

from diagrams.onprem.container import Docker
from diagrams.programming.language import Python

with Diagram("AB Framework", show=False):
    ingress = Nginx("nginx")

    metrics = Prometheus("metric")
    metrics << Grafana("monitoring")

    with Cluster("WSGI server"):
        gunicorn = Gunicorn("gunicorn")

        flask = [
            Flask(""),
            Flask(""),
            Flask("")
        ]

    with Cluster("data source"):
        datasource = Mysql("mysql")
        datasource - Redis("redsi") - Hive("hive")

    with Cluster("engine"):
        engine = Python("python")
        engine - Spark("spark")

    aggregator = Fluentd("logging")

    engine >> aggregator

    flask - Edge(color="brown") >> datasource >> engine << metrics
    flask - Edge(color="gray") >> engine

    ingress >> gunicorn >> flask
