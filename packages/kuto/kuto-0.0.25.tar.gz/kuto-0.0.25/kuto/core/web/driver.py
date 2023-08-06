"""
@Author: kang.yang
@Date: 2023/5/12 20:49
"""
import os
import time

import allure
from playwright.sync_api import sync_playwright, expect

from kuto.testdata import get_int
from kuto.utils.exceptions import ScreenFailException
from kuto.utils.log import logger


class PlayWrightDriver:

    def __init__(self, browserName: str, headless: bool = False, state: dict = None):
        self.browserName = browserName
        self.headless = headless

        self.playwright = sync_playwright().start()
        if browserName == 'firefox':
            self.browser = self.playwright.firefox.launch(headless=headless)
        elif browserName == 'webkit':
            self.browser = self.playwright.webkit.launch(headless=headless)
        else:
            self.browser = self.playwright.chromium.launch(headless=headless)
        if state:
            self.context = self.browser.new_context(storage_state=state, no_viewport=True)
        else:
            self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def switch_tab(self, locator):
        logger.info("new tab")
        with self.page.expect_popup() as popup_info:
            locator.click()
        self.page = popup_info.value

    def visit(self, url):
        logger.info(f"visit: {url}")
        self.page.goto(url)

    def storage_state(self, path=None):
        logger.info("save state")
        if not path:
            raise ValueError("path can not be None.")
        self.context.storage_state(path=path)

    def set_cookies(self, cookies: list):
        logger.info("add cookies and reload")
        self.context.add_cookies(cookies)
        self.page.reload()

    def screenshot(self, file_name=None, with_time=True):
        """
        截图并保存到预定路径
        @param with_time: 是否带时间戳
        @param file_name: foo.png or fool
        @return:
        """
        logger.info("screenshot")
        if not file_name:
            raise ValueError("file_name should not be None.")

        try:
            # 把文件名处理成test.png的样式
            if "." in file_name:
                file_name = file_name.split(r".")[0]
            # 截图并保存到当前目录的images文件夹中
            relative_path = "screenshots"
            if os.path.exists(relative_path) is False:
                os.mkdir(relative_path)
            if with_time:
                time_str = time.strftime(f"%Y-%m-%d_%H_%M_%S_{get_int(min_size=1, max_size=1000)}")
                file_name = f"{time_str}_{file_name}.png"
            else:
                file_name = f'{file_name}.png'
            file_path = os.path.join(relative_path, file_name)
            logger.info(f"save to: {os.path.join(relative_path, file_name)}")
            self.page.screenshot(path=file_path, full_page=True)
            # 上传allure报告
            allure.attach.file(
                file_path,
                attachment_type=allure.attachment_type.PNG,
                name=f"{file_name}",
            )
            return file_path
        except Exception as e:
            raise ScreenFailException(f"screen failed: \n{str(e)}")

    def close(self):
        logger.info("close browser")
        self.page.close()
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def assert_title(self, title: str):
        logger.info("assert title")
        expect(self.page).to_have_title(title)

    def assert_url(self, url: str):
        logger.info("assert url")
        expect(self.page).to_have_url(url)
