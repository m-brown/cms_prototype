import os
import unittest

from cms_prototype.tests.common import TestCase

class VersionedDocumentTestCase(TestCase):

    def setUp(self):
        super(VersionedDocumentTestCase, self).setUp()
        from cms_prototype.models.base import VersionedDocument

        self.db = VersionedDocument._get_collection().database
        self.db.versioned_document.remove()
        self.db.versioned_versioned_document.remove()

    def test_single_revision(self):
        from cms_prototype.models.base import VersionedDocument
        v = VersionedDocument()
        v.save()
        vid = v.to_mongo()['_id']
        q = self.db.versioned_document.find()
        self.assertEqual(q.count(), 1)
        q = self.db.versioned_document.find({'_id': vid})
        self.assertEqual(q.count(), 1)
        q = self.db.versioned_versioned_document.find()
        self.assertEqual(q.count(), 1)
        q = self.db.versioned_versioned_document.find({'_id.id': vid})
        self.assertEqual(q.count(), 1)
