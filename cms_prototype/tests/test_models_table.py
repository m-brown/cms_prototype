from cms_prototype.tests.common import TemplateTestCase
from cms_prototype.models.blocks.table import MongoEngineTable, MongoColumn
from cms_prototype.models.blocks.block import Block


class MongoEngineTableTest(TemplateTestCase):
    def setUp(self):
        super(MongoEngineTableTest, self).setUp()
        self.db = MongoEngineTable._get_collection().database

        self.db.block.remove()
        self.db.versioned_block.remove()

    def test_creation_and_population(self):
        t = MongoEngineTable(database=self.db.name, collection='block')
        t.save()
        t.populate({})

        self.assertNotEqual(t.data, None)
        self.assertEqual(len(t.data), 1)

    def test_multiple_rows(self):
        t = MongoEngineTable(database=self.db.name, collection='block')
        t.save()
        t.populate({})

        self.assertNotEqual(t.data, None)
        self.assertEqual(len(t.data), 1)

        b = Block(name='test')
        b.save()

        t.populate({})
        self.assertNotEqual(t.data, None)
        self.assertEqual(len(t.data), 2)

        b = Block(name='test2')
        b.save()

        t.populate({})
        self.assertNotEqual(t.data, None)
        self.assertEqual(len(t.data), 3)

    def test_render(self):
        t = MongoEngineTable(database=self.db.name, collection='block')
        t.save()

        a = MongoEngineTable.objects(id=t.id).first()
        a.populate({})

        html = a.render()

        self.assertNotEqual(html, '')
        self.assertIn('<table', html)
        self.assertEqual(html.count('<tr>'), 1)

    def test_render_columns(self):
        t = MongoEngineTable(database=self.db.name, collection='block', name='test table')
        t.columns.append(MongoColumn(field='name', display='Name'))
        t.columns.append(MongoColumn(field='_cls', display='Class'))
        t.save()

        t.populate({})
        html = t.render()

        self.assertIn('<table', html)
        self.assertEqual(html.count('<tr>'), 1)
        self.assertEqual(html.count('<th>'), 2)
        self.assertEqual(html.count('<td>'), 2)

    def test_render_nopopulate(self):
        t = MongoEngineTable(database=self.db.name, collection='block')
        t.save()

        html = t.render()
        self.assertNotEqual(html, '')
        self.assertEqual(html.count('<tr>'), 1)

    def test_sort(self):
        t = MongoEngineTable(database=self.db.name, collection='block', name='table', sort={'name': 1})
        t.columns.append(MongoColumn(field='name', display='Name'))
        t.save()

        b2 = Block(name='test2')
        b2.save()
        b3 = Block(name='test3')
        b3.save()
        b1 = Block(name='test1')
        b1.save()

        t.populate({})
        self.assertEqual(len(t.data), 4)
        self.assertEqual(t.data[0]['name'], 'table')
        self.assertEqual(t.data[3]['name'], 'test3')

        #test reverse order
        t.sort = {'name': -1}
        t.save()
        t.populate({})
        self.assertEqual(len(t.data), 4)
        self.assertEqual(t.data[0]['name'], 'test3')
        self.assertEqual(t.data[3]['name'], 'table')

    def test_query(self):
        t = MongoEngineTable(database=self.db.name, collection='block', name='table', spec={'name': 'name'})
        t.save()
        t.populate({'name': 'table'})

        self.assertNotEqual(t.data, None)
        self.assertEqual(len(t.data), 1)

        b = Block(name='test')
        b.save()

        t.populate({'name': 'table'})
        self.assertNotEqual(t.data, None)
        self.assertEqual(len(t.data), 1)
