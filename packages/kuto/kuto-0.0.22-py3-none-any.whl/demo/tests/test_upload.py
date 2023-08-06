"""
@Author: kang.yang
@Date: 2023/5/17 11:05
"""
import pyautogui

import kuto
from kuto import WebElem

from demo.tests.test_web import LoginFunc


def upload_file(file_path):
    pyautogui.write(file_path)
    pyautogui.press('enter', 3)


class BatchSearchPage(kuto.Page):
    uploadBtn = WebElem(css='#__layout > div > div.search-advance-container_wraper > div > div.search-container '
                            '> div > div:nth-child(1) > div.left-footer > div.op-bar > div.upload-btn > span:nth-child(1)')
    matchBtn = WebElem(css='#__layout > div > div.search-advance-container_wraper > div > div.search-container > div '
                           '> div:nth-child(1) > div.left-footer > div.op-bar > div.search-btn > button.el-button.el-button--primary')


class TestUpload(kuto.TestCase):

    def start(self):
        self.loginFunc = LoginFunc(self.driver)
        self.batchPage = BatchSearchPage(self.driver)

    def test_1(self):
        self.loginFunc.login_with_pwd("xxx", "xxx")
        self.open("https://patents.qizhidao.com/search/batchProcess?tab=advance")
        self.batchPage.uploadBtn.click()
        upload_file("/Users/UI/Downloads/upload.xlsx")
        self.batchPage.matchBtn.click()
        self.sleep(5)
        self.driver.screenshot("匹配结果")


if __name__ == '__main__':
    kuto.main(platform="web", host="https://www.qizhidao.com")
