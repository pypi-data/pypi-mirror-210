import inspect
import json
import os

import pytest

from kuto.utils.config import config
from kuto.utils.log import logger


class TestMain(object):
    """
    Support for app、web、http
    """
    def __init__(self,
                 did: str = None,
                 pkg: str = None,
                 browser: str = None,
                 headless: bool = False,
                 path: str = None,
                 rerun: int = 0,
                 xdist: bool = False,
                 host: str = None,
                 headers: dict = None,
                 state: dict = None,
                 cookies: list = None
                 ):
        """
        @type state: 通过playwright的storage_state方法获取
        @type cookies:
        @param did: 设备id，针对安卓和ios
        @param pkg: 应用包名，针对安卓和ios
        @param browser: 浏览器类型，chrome、firefox、webkit
        @param path: 用例目录，None默认代表当前文件
        @param rerun: 失败重试次数
        @param xdist: 并发支持
        @param host: 域名，针对接口和web
        @param headers: {
            "login": {},
            "visit": {}
        }
        """

        # 公共参数保存
        if browser:
            platform = "web"
        elif did:
            if "-" in did:
                platform = "ios"
            else:
                platform = "android"
        else:
            platform = "api"
        config.set_common("platform", platform)
        # api参数保存
        config.set_api("base_url", host)
        if headers:
            if 'login' not in headers.keys():
                raise KeyError("without login key!!!")
            login_ = headers.pop('login', {})
            config.set_api('login', login_)
            visit_ = headers.pop('visit', {})
            config.set_api('visit', visit_)
        # app参数保存
        config.set_app("device_id", did)
        config.set_app("pkg_name", pkg)
        # config.set_app("errors", errors)
        # web参数保存
        config.set_web("base_url", host)
        config.set_web("browser_name", browser)
        config.set_web("headless", headless)
        if state:
            config.set_web("state", json.dumps(state))
        if cookies:
            config.set_web("cookies", json.dumps(cookies))

        # 执行用例
        logger.info('执行用例')
        if path is None:
            stack_t = inspect.stack()
            ins = inspect.getframeinfo(stack_t[1][0])
            file_dir = os.path.dirname(os.path.abspath(ins.filename))
            file_path = ins.filename
            if "\\" in file_path:
                this_file = file_path.split("\\")[-1]
            elif "/" in file_path:
                this_file = file_path.split("/")[-1]
            else:
                this_file = file_path
            path = os.path.join(file_dir, this_file)
        cmd_list = [
            '-sv',
            '--reruns', str(rerun),
            '--alluredir', 'reports', '--clean-alluredir'
        ]
        if path:
            cmd_list.insert(0, path)
        if xdist:
            """仅支持http接口测试和web测试，并发基于每个测试类，测试类内部还是串行执行"""
            cmd_list.insert(1, '-n')
            cmd_list.insert(2, 'auto')
        logger.info(cmd_list)
        pytest.main(cmd_list)

        # 公共参数保存
        config.set_common("platform", "api")
        # api参数保存
        config.set_api("base_url", None)
        config.set_api('login', {})
        config.set_api('visit', {})
        # app参数保存
        config.set_app("device_id", None)
        config.set_app("pkg_name", None)
        # config.set_app("errors", [])
        # web参数保存
        config.set_web("base_url", None)
        config.set_web("browser_name", "chrome")
        config.set_web("headless", False)
        config.set_web("state", None)
        config.set_web("cookies", None)


main = TestMain


if __name__ == '__main__':
    main()

