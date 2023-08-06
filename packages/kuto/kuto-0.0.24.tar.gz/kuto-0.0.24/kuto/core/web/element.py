"""
@Author: kang.yang
@Date: 2023/5/13 10:16
"""
import time

from kuto.utils.exceptions import NoSuchElementException
from kuto.utils.log import logger
from kuto.core.web.driver import PlayWrightDriver
from playwright.sync_api import expect


class WebElem:
    """
    通过selenium定位的web元素
    """

    def __init__(self,
                 driver: PlayWrightDriver = None,
                 xpath: str = None,
                 css: str = None,
                 text: str = None,
                 placeholder: str = None,
                 index: int = None
                 ):
        """

        @param driver: 浏览器驱动
        @param xpath: 根据xpath进行定位
        @param css: 根据css selector进行定位
        @param text:
        @param placeholder:
        """
        self._driver = driver
        self._xpath = xpath
        self._css = css
        self._text = text
        self._placeholder = placeholder
        self._index = index

    def __get__(self, instance, owner):
        if instance is None:
            return None

        self._driver = instance.driver
        return self

    def find_element(self):
        element = None
        if self._text:
            logger.info(f"try find text: {self._text}")
            element = self._driver.page.get_by_text(self._text)
        if self._placeholder:
            logger.info(f"try find placeholder: {self._placeholder}")
            element = self._driver.page.get_by_placeholder(self._placeholder)
        if self._css:
            logger.info(f"try find css: {self._css}")
            element = self._driver.page.locator(self._css)
        if self._xpath:
            logger.info(f"try find xpath: {self._xpath}")
            element = self._driver.page.locator(self._xpath)
        if self._index:
            element = element.nth(self._index)
        return element

    def fail_handler(self):
        logger.info("loc fail")
        self._driver.screenshot("loc_fail")
        raise NoSuchElementException(f"[elem loc fail]")

    def click(self, timeout=10):
        logger.info("click")
        try:
            self.find_element().click(timeout=timeout*1000)
        except:
            self.fail_handler()

    def input(self, text, timeout=10):
        logger.info("input")
        try:
            self.find_element().fill(text, timeout=timeout*1000)
        except:
            self.fail_handler()

    def check(self, timeout=10):
        logger.info("check")
        try:
            self.find_element().check(timeout=timeout*1000)
        except:
            self.fail_handler()

    def select(self, value: str, timeout=10):
        logger.info("select")
        try:
            self.find_element().select_option(value, timeout=timeout*1000)
        except:
            self.fail_handler()

    def text(self):
        logger.info("get text")
        return self.find_element().text_content()

    def assert_visible(self):
        logger.info("assert visible")
        expect(self.find_element()).to_be_visible()

    def assert_hidden(self):
        logger.info("assert hidden")
        expect(self.find_element()).to_be_hidden()

    def assert_contain(self, text: str):
        logger.info("assert contain text")
        expect(self.find_element()).to_contain_text(text)

    def assert_have_text(self, text: str):
        logger.info("assert have text")
        expect(self.find_element()).to_have_text(text)


class FraElem(WebElem):

    def __init__(self, driver: PlayWrightDriver = None, frame: str = None, xpath: str = None, css: str = None,
                 text: str = None, placeholder: str = None, index: int = None):
        """

        @param driver: 浏览器驱动
        @type frame: frame定位方式，使用正常的css定位方式即可
        @param xpath: 根据xpath进行定位
        @param css: 根据css selector进行定位
        @param text: 根据标签的文本定位
        @param placeholder: 根据输入框的placeholder定位
        """
        super().__init__(driver, xpath, css, text, placeholder, index)
        self._driver = driver
        self._frame_loc = frame
        self._xpath = xpath
        self._css = css
        self._text = text
        self._placeholder = placeholder
        self._index = index

    def find_element(self):

        element = None
        if self._text:
            logger.info(f"try find text: {self._text} in iframe {self._frame_loc}")
            element = self._driver.page.frame_locator(self._frame_loc).get_by_text(self._text)
        if self._placeholder:
            logger.info(f"try find placeholder: {self._placeholder} in iframe {self._frame_loc}")
            element = self._driver.page.frame_locator(self._frame_loc).get_by_placeholder(self._placeholder)
        if self._css:
            logger.info(f"try find css: {self._css} in iframe {self._frame_loc}")
            element = self._driver.page.frame_locator(self._frame_loc).locator(self._css)
        if self._xpath:
            logger.info(f"try find xpath: {self._xpath} in iframe {self._frame_loc}")
            element = self._driver.page.frame_locator(self._frame_loc).locator(self._xpath)
        if self._index:
            element = element.nth(self._index)
        return element
