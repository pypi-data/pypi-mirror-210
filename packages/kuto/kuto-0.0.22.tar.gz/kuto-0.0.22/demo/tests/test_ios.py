import kuto
from kuto import IosElem


class IndexPage(kuto.Page):
    """首页"""
    ad = IosElem(text='close white big')
    my = IosElem(text='我的')


class MyPage(kuto.Page):
    """我的页"""
    setting = IosElem(text='settings navi')


class TestSearch(kuto.TestCase):
    """设置页测试"""

    def start(self):
        self.index_page = IndexPage(self.driver)
        self.my_page = MyPage(self.driver)

    def test_1(self):
        """进入设置页"""
        self.index_page.ad.click_exists(timeout=5)
        self.index_page.my.click()
        self.my_page.setting.click()


if __name__ == '__main__':
    kuto.main(did='00008101-000E646A3C29003A', pkg='com.qizhidao.company')

