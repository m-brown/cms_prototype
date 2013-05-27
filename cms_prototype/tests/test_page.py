from pyramid import testing
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from cms_prototype.tests.common import TestCase
from cms_prototype.models.site import Site, Page, Url
from cms_prototype.models.page_handler import PageHandler
from cms_prototype.views.page import page


class PageloadTest(TestCase):

    def setUp(self):
        super(PageloadTest, self).setUp()

        site = Site(name='test', unique_name='test')
        site.save()
        page = Page(name='test')
        page.save()
        url = Url(site=site, url='index.html', page=page)
        url.save()

        from cms_prototype import main
        app = main()

    def test_missing_project(self):
        request = testing.DummyRequest(matchdict={'site_unique_name': 'somerandomprojectthatdoesnotexist'})
        try:
            page(request)
        except HTTPFound as redirect:
            self.assertEquals(redirect.location, '/somerandomprojectthatdoesnotexist/_editor/notfound?site_unique_name=somerandomprojectthatdoesnotexist')
        else:
            self.fail()

    def test_missing_page(self):
        request = testing.DummyRequest(matchdict={'site_unique_name': 'test', 'url': 'somerandompagethatdoesnotexist.html'})

        with self.assertRaises(HTTPNotFound):
            page(request)

    def test_missing_page_in_editor(self):
        from cms_prototype.views.page import editor
        request = testing.DummyRequest(matchdict={'site_unique_name': 'test', 'url': 'somerandompagethatdoesnotexist.html'})

        site = Site(name='editor', unique_name='_editor')
        site.save()

        try:
            editor(request)
        except HTTPFound as redirect:
            self.assertEquals(redirect.location, '/test/_editor/page?url=somerandompagethatdoesnotexist.html')
        else:
            self.fail()

    def test_page_load(self):
        request = testing.DummyRequest(matchdict={'site_unique_name': 'test', 'url': 'index.html'})
        response = page(request)

        self.assertEquals(response.status_code, 200)

    def test_page_load_just_site(self):
        from cms_prototype.views.page import site_nopage
        request = testing.DummyRequest(matchdict={'site_unique_name': 'test'})
        response = site_nopage(request)

        self.assertEquals(response.status_code, 200)


class DummyHandler(PageHandler):
    def pre_block_process(self):
        return


class PageHandlerLoadTest(TestCase):
    def setUp(self):
        super(PageHandlerLoadTest, self).setUp()

        site = Site(name='test', unique_name='test')
        site.save()
        page = Page(name='test', handler_module='cms_prototype.tests.test_page', handler_class='DummyHandler')
        page.save()
        url = Url(site=site, url='index.html', page=page)
        url.save()

        from cms_prototype import main
        app = main()

    def test_handler_view(self):
        request = testing.DummyRequest(matchdict={'site_unique_name': 'test', 'url': 'index.html'})
        response = page(request)

        self.assertEquals(response.status_code, 200)
