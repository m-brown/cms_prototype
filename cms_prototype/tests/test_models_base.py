import unittest
from pymongo import MongoClient

class VersionedDocument(unittest.TestCase):
	def setUp(self):
		connection = MongoClient('localhost', 27017)
		self.db = connection.local
		self.db.versioned_document.remove()
		self.db.versioned_versioned_document.remove()

	def test_single_revision(self):
		from cms_prototype.models.base import VersionedDocument
		v = VersionedDocument()
		v.save()
		q = self.db.versioned_document.find()
		self.assertEqual(q.count(), 1)
		q = self.db.versioned_document.find({'_id': v.to_mongo()['_id']})
		self.assertEqual(q.count(), 1)