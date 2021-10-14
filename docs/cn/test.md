

# 测试用例 

## 关于pytest和tox
[pytest](https://docs.pytest.org/en/latest/)是一个自动化测试框架； 
[tox](https://tox.readthedocs.io/en/latest/)可以启动一个venv然后执行各种脚本。其支持多进程，测试速度很快。

两者结合就可以实现启动一个venv然后跑pytest执行测试脚本。

目前默认启动了8个线程进行测试。

#### 开发测试用例
要求：
1. 测试代码统一放在`tests`目录下，文件以`test_`开头，测试函数以`test_`开头。这是pytest的要求
2. 把`tests/__init__.py`和`tox.ini`复制到新项目里。
   注意一定要保留`tests/__init__.py`文件，否则会报错
3. 接口测试函数接受`client`参数，调用get_data/post_data函数来模拟用户的get/post请求。要求每一个接口要有至少一个接口测试函数
4. 目前pytest默认使用'gs1/gs1'用户登录并执行测试。如果需要使用其他用户，需要新建`tests/conftest.py`文件，并添加如下内容：

```python
import pytest


@pytest.fixture(scope="session")
def login_info():
    return {'username': 'YOUR_USERNAME', 'password': 'YOUR_PASSWORD'}
```

#### 执行测试
1. `pip3 install tox pytest`
1. 执行单个测试文件可以在**根目录下**手动执行`pytest -e CONFIG -s --disable-warnings tests/xxx.py`。

   `-e`：载入哪个配置文件。比如`-e dev`代表载入`config/config_dev.py`. Since v2.5.0
   
   `-s`：显示控制台和logger日志
   
   `--disable-warnings`: 忽略警告
1. 运行所有测试用例可以在项目**根目录**下执行`tox`命令即可

** 执行测试用例不需要手动启动服务，测试框架会自己启起来。 **

** 使用多进程测试的话需要配置redis，否则会登录失败。 **


