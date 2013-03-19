from cms_prototype.tests.common import TemplateTestCase
from cms_prototype.models.table import MongoTable


class MongoTableTest(TemplateTestCase):
    def setUp(self):
        super(MongoTableTest, self).setUp()
        self.db = MongoTable._get_collection().database

        self.db.block.remove()
        self.db.versioned_block.remove()

    def test_creation_and_population(self):
        t = MongoTable(database=self.db.name, collection='block')
        t.save()
        t.populate()

        self.assertNotEqual(t.cursor, None)
        self.assertEqual(t.cursor.count(), 1)

    def test_render(self):
        t = MongoTable(database=self.db.name, collection='block')
        t.save()

        a = MongoTable.objects(id=t.id).first()

        self.assertNotEqual(a.render(), '')
