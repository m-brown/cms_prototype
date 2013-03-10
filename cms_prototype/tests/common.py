import os

from mongoengine import connect
from pyramid import testing
#from pyramid.mako_templating import renderer_factory

from unittest import TestCase as _TestCase

class TestCase(_TestCase):

    def setUp(self):
        connect('cms', host=os.getenv('DB_HOST', 'localhost'))

class TemplateTestCase(TestCase):

    def setUp(self):
        super(TemplateTestCase, self).setUp()

        self.config = testing.setUp()
        self.config.add_settings({'mako.directories': 'cms_prototype:templates'})
        self.config.include('pyjade.ext.pyramid')
