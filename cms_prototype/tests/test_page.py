import unittest
from cms_prototype.tests.common import TestCase

from cms_prototype.models.site import Site, Page, UrlKey, Url

class PageloadTest(TestCase):
    def setUp(self):
        super(PageloadTest, self).setUp()
        self.db = Site._get_collection().database

        site = Site(name='test', unique_name='test')
        site.save()
        page = Page()
        page.save()
        urlKey = UrlKey(site=site, url='index.html')
        url = Url(key=urlKey, page=page)
        url.save()

        from cms_prototype import main
        app = main()
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_missing_project(self):
        res = self.testapp.get('/somerandomprojectthatdoesnotexist/', status=404)
        self.assertTrue('Not Found' in res.body)

    def test_missing_page(self):
        res = self.testapp.get('/test/somerandompagethatdoesnotexist.html', status=404)
        self.assertTrue('Not Found' in res.body)

	def test_page_load(self):
		res = self.testapp.get('/test/index.html', status=200)