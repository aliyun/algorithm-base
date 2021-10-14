"""
日常环境配置
"""

PORT = 8000

workers = 4
# max_requests = 2
# max_requests_jitter = 1
# preload_app = False

# keepalive = 2

timeout = 5

APP_NAME = 'simple'
# REGISTER_AT_EUREKA = True
# EUREKA_SERVER = "http://127.0.0.1:7001/eureka/"

preload_app = False

# 是否开启存活检查
ENABLE_LIVENESS_PROB = True
LIVENESS_PROB = {
    # 容器启动后要等待多少秒后存活和就绪探测器才被初始化，最小值是 0。
    "initialDelaySeconds": 2,
    # 执行探测的时间间隔（单位是秒）。最小值是 1。
    "periodSeconds": 5,
    # 探测的超时后等待多少秒。最小值是 1。
    "timeoutSeconds": 1,
    # 当连续失败N次后，重启容器
    "failureThreshold": 3,
}
