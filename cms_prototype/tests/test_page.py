from pyramid import testing
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from cms_prototype.tests.common import TestCase
from cms_prototype.models.site import Site, Page, Url
from cms_prototype.models.page_handler import PageHandler


class PageloadTest(TestCase):

    def setUp(self):
        super(PageloadTest, self).setUp()

        site = Site(name='test', unique_name='test')
        site.save()
        page = Page()
        page.save()
        url = Url(site=site, url='index.html', page=page)
        url.save()

        from cms_prototype import main
        app = main()

    def test_missing_project(self):
        from cms_prototype.views.page import page

        request = testing.DummyRequest(matchdict={'site_unique_name': 'somerandomprojectthatdoesnotexist'})
        try:
            page(request)
        except HTTPFound as redirect:
            self.assertEquals(redirect.location, '/somerandomprojectthatdoesnotexist/_editor/notfound')
        else:
            self.fail()

    def test_missing_page(self):
        from cms_prototype.views.page import page
        request = testing.DummyRequest(matchdict={'site_unique_name': 'test', 'url': 'somerandompagethatdoesnotexist.html'})

        with self.assertRaises(HTTPNotFound):
            page(request)

    def test_page_load(self):
        from cms_prototype.views.page import page
        request = testing.DummyRequest(matchdict={'site_unique_name': 'test', 'url': 'index.html'})
        response = page(request)

        self.assertEquals(response.status_code, 200)


class DummyHandler(PageHandler):
    def pre_block_process(self):
        return


class PageHandlerLoadTest(TestCase):
    def setUp(self):
        super(PageHandlerLoadTest, self).setUp()

        site = Site(name='test', unique_name='test')
        site.save()
        page = Page(handler_module='cms_prototype.tests.test_page', handler_class='DummyHandler')
        page.save()
        url = Url(site=site, url='index.html', page=page)
        url.save()

        from cms_prototype import main
        app = main()

    def test_handler_view(self):
        from cms_prototype.views.page import page
        request = testing.DummyRequest(matchdict={'site_unique_name': 'test', 'url': 'index.html'})
        response = page(request)

        self.assertEquals(response.status_code, 200)
