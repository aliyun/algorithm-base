## 算法框架v2

### prometheus 监控指标
目前的监控指标主要用于直观判断服务状态，协助debug用，贵精不贵多。
基本的思想是来到系统的事件，比如http请求都要记录;系统的一些关键逻辑/函数等也要记录；
从系统发出的事件，比如db访问、对其他系统的接口调用等也要记录。

除上述指标之外，各个项目也应该根据自身需求记录特有的指标，比如进程池大小、等待某一关键资源的线程数等。

#### http相关
黑盒指标，用于记录来的http请求相关信息

1. counter http_requests_total(method, url, code)
记录每个http接口的访问总数
method：GET/POST/PUT/DELETE
url：访问的哪个url，只记录path部分即可，无需带上参数
code：接口的返回值 (200/500等）

2. histogram http_request_duration_seconds(method, url)
记录每个http接口的处理时间
method：GET/POST/PUT/DELETE
url：访问的哪个url

3. gauge inprogress_http_requests(method, url)
记录同时有多少http请求在处理
method：GET/POST/PUT/DELETE
url：访问的哪个url

#### 关键函数/方法相关
白盒指标，用于记录一些关键函数/方法的指标，以及一些向外部发送的请求，比如db访问、其他系统的远程调用等。

1. counter func_call_errors_total(name)
记录有多少函数/方法异常
name：函数名

2. counter func_calls_total(name)
记录有多少函数/方法请求
name：函数名

3. histogram func_call_duration_seconds(name)
函数/方法总处理时间
name：函数名

4. gauge inprogress_func_calls(name)
有多少函数/方法在处理
name：函数名
