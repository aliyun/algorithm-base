# 错误和异常

## 正常
http返回值200，response code为0

## 消息
http返回值为200，response code为-100。
```
raise Message(msg="the error is caused by xxx")
返回值：
{
code: -100,
data: "the error is caused by xxx"
}
```

## 有堆栈异常

### 第一种异常

http返回值为500，response code为-1,返回错误堆栈。 
```
i = 1 / 0
返回值：
{
code: -1,
data: [
"Traceback (most recent call last): ",
" File "/Users/peng/miniconda3/envs/ab/lib/python3.7/site-packages/flask/app.py", line 1950, in full_dispatch_request rv = self.dispatch_request() ",
" File "/Users/peng/miniconda3/envs/ab/lib/python3.7/site-packages/flask/app.py", line 1936, in dispatch_request return self.view_functions[rule.endpoint](**req.view_args) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/utils/prometheus.py", line 30, in inner ret = func(*args, **kwargs) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/controllers/algorithm.py", line 119, in run_algorithm_backend return run_algorithm(body) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/controllers/algorithm.py", line 101, in run_algorithm result = algorithm.run_algorithm(request_body) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/services/algorithm.py", line 19, in run_algorithm result = task.run() ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/utils/task.py", line 141, in run ret = self.run_algorithm() ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/utils/task.py", line 121, in run_algorithm result = self.algorithm.run(self.kwargs) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/utils/algorithm.py", line 52, in run ret = self.main(*main_args) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/utils/prometheus.py", line 61, in inner return func(*args, **kwargs) ",
" File "/Users/peng/Documents/project/algorithm-base-demos/simple/algorithms/demo.py", line 29, in unknown print(1 / 0) ",
"ZeroDivisionError: division by zero "
]
}
```

### 第二种异常
不指定data属性，默认将堆栈附带到返回值中
```
raise AlgorithmException()
返回值：
{
code: -1,
data: [
"Traceback (most recent call last): ",
" File "/Users/peng/miniconda3/envs/ab/lib/python3.7/site-packages/flask/app.py", line 1950, in full_dispatch_request rv = self.dispatch_request() ",
" File "/Users/peng/miniconda3/envs/ab/lib/python3.7/site-packages/flask/app.py", line 1936, in dispatch_request return self.view_functions[rule.endpoint](**req.view_args) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/utils/prometheus.py", line 30, in inner ret = func(*args, **kwargs) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/controllers/algorithm.py", line 119, in run_algorithm_backend return run_algorithm(body) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/controllers/algorithm.py", line 101, in run_algorithm result = algorithm.run_algorithm(request_body) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/services/algorithm.py", line 19, in run_algorithm result = task.run() ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/utils/task.py", line 141, in run ret = self.run_algorithm() ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/utils/task.py", line 121, in run_algorithm result = self.algorithm.run(self.kwargs) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/utils/algorithm.py", line 52, in run ret = self.main(*main_args) ",
" File "/Users/peng/Documents/project/algorithm-base/src/ab/utils/prometheus.py", line 61, in inner return func(*args, **kwargs) ",
" File "/Users/peng/Documents/project/algorithm-base-demos/simple/algorithms/demo.py", line 29, in unknown print(1 / 0) ",
"ZeroDivisionError: division by zero "
]
}
```


## 无堆栈异常
http返回值为500，respons code为-1,不返回错误堆栈。
```
raise AlgorithmException(data="this is an exception")
返回值：
{
code: -1,
data: "this is an exception"
}
```
