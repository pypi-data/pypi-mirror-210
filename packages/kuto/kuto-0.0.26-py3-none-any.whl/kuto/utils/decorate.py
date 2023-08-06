"""
使用allure需要下载，并配置到环境变量，下载地址：https://github.com/allure-framework/allure2/releases
"""
import pytest


def order(index):
    """
    指定用例执行顺序, pip install pytest-ordering==0.6
    doc: https://blog.csdn.net/weixin_43880991/article/details/116221362
    """
    return pytest.mark.run(order=index)


def depend(depends: list or str = None, name=None):
    """
    设置用例依赖关系, pip install pytest-dependency==0.5.1
    doc: https://www.cnblogs.com/se7enjean/p/13513131.html
    """
    if isinstance(depends, str):
        depends = [depends]
    return pytest.mark.dependency(name=name, depends=depends)


# 参数化数据
def data(list_data: list):
    """
    必须传入一个list，使用时通过在参数列表传入parma进行调用
    """
    return pytest.mark.parametrize('param', list_data)


