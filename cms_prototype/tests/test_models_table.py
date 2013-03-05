from cms_prototype.tests.common import TestCase
from cms_prototype.models.table import MongoTable


class MongoTableTest(TestCase):
    def setUp(self):
        super(MongoTableTest, self).setUp()
        self.db = MongoTable._get_collection().database

        self.db.block.remove()
        self.db.versioned_block.remove()

    def test_creation(self):
        t = MongoTable(database=self.db, collection='block')
        t.populate()

        self.assertNotEqual(t.cursor, None)
