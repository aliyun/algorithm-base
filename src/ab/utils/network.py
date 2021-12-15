import socket
import py_eureka_client.http_client as http_client


# the method below is copied from eureka python sdk.
# https://github.com/keijack/python-eureka-client
def get_instance_ip(server):
    url_obj = http_client.parse_url(server)
    target_ip = url_obj["host"]
    target_port = url_obj["port"]
    if target_port is None:
        if url_obj["schema"] == "http":
            target_port = 80
        else:
            target_port = 443

    if url_obj["ipv6"] is not None:
        target_ip = url_obj["ipv6"]
        socket_family = socket.AF_INET6
    else:
        socket_family = socket.AF_INET

    s = socket.socket(socket_family, socket.SOCK_DGRAM)
    s.connect((target_ip, target_port))
    ip = s.getsockname()[0]
    s.close()
    return ip
