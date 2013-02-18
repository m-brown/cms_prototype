import unittest
from cms_prototype.models.base import VersionedDocument

class VersionedDocument(unittest.TestCase):
	def setUp(self):
		connection = MongoClient('localhost', 27017)
		self.db = connection.local
		self.db.versioneddocument.remove()

	def test_single_revision(self):
		v = VersionedDocument()
		q = self.db.versioneddocument.find({'_id': v._id})
		self.assertEqual(q.length, 1)