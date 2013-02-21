import os
import unittest

from mongoengine import StringField
from cms_prototype.models.base import VersionedDocument
from cms_prototype.tests.common import TestCase

class SomeTestDocument(VersionedDocument):
    some_key = StringField(max_length=50)

class VersionedDocumentTestCase(TestCase):

    def setUp(self):
        super(VersionedDocumentTestCase, self).setUp()
        self.db = SomeTestDocument._get_collection().database
        self.db.some_test_document.remove()
        self.db.versioned_some_test_document.remove()

    def test_single_revision(self):
        test_doc = SomeTestDocument(some_key='test value')
        test_doc.save()

        vid = test_doc.id
        q = self.db.some_test_document.find()
        self.assertEqual(q.count(), 1)
        q = self.db.some_test_document.find({'_id': vid})
        self.assertEqual(q.count(), 1)
        q = self.db.versioned_some_test_document.find()
        self.assertEqual(q.count(), 1)
        q = self.db.versioned_some_test_document.find({'_id.id': vid})
        self.assertEqual(q.count(), 1)

    def test_compound_key_revision(self):
    	from cms_prototype.models.site import Site, Url, UrlKey

    	site = Site(name='@UK', unique_name='uk-plc')
    	site.save()

    	url = Url(key=UrlKey(url='/index.html', site=site))
    	url.save()
