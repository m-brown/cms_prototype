import os
from pyramid import testing
from mongoengine import connect
from unittest import TestCase as _TestCase


class TestCase(_TestCase):

    def setUp(self):
        connect('cms', host=os.getenv('DB_HOST', 'localhost'))
        from cms_prototype.models.base import VersionedDocument
        self.db = VersionedDocument._get_db()
        self.db.connection.drop_database('cms')


class TemplateTestCase(TestCase):

    def setUp(self):
        super(TemplateTestCase, self).setUp()

        self.config = testing.setUp()
        self.config.add_settings({'mako.directories': 'cms_prototype:templates'})

        mako_mod_directory = os.getenv('MAKO_MOD_DIRECTORY')
        if mako_mod_directory:
            self.config.add_settings({'mako.module_directory': mako_mod_directory})
        self.config.include('pyjade.ext.pyramid')
