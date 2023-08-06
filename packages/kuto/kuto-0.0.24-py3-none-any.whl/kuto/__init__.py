from kuto.core.api.request import HttpReq
from kuto.core.android.element import AdrElem
from kuto.core.android.driver import AndroidDriver
from kuto.core.ios.element import IosElem
from kuto.core.ios.driver import IosDriver
from kuto.core.web.element import WebElem, FraElem
from kuto.core.web.driver import PlayWrightDriver
from kuto.case import TestCase, Page
from kuto.running.runner import main
from kuto.utils.config import config
from kuto.utils.decorate import data
from kuto.utils.log import logger


__version__ = "0.0.24"
__description__ = "移动、web、接口自动化测试框架"
