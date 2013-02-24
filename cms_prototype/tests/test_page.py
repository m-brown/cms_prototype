import unittest
from cms_prototype.tests.common import TestCase

from cms_prototype.models.site import Site, Page, UrlKey, Url

class PageloadTest(TestCase):
	def setUp(self):
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

	def test_page_load(self):
		response = self.testapp.get('/test/index.html')