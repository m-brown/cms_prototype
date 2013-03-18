from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from cms_prototype.tests.common import TestCase
from cms_prototype.models.site import Block
from cms_prototype.models.table import MongoTable, MongoColumn
from bson.objectid import ObjectId


class BlockViewTest(TestCase):

    def setUp(self):
        super(BlockViewTest, self).setUp()
        self.config = testing.setUp()
        self.db = Block._get_collection().database

        self.db.block.remove()
        self.db.versioned_block.remove()

        b = Block(name='test')
        b.save()
        self.block_id = b.id

    def test_missing_block(self):
        from cms_prototype.views.block import block

        request = testing.DummyRequest(matchdict={'block': ObjectId()})

        with self.assertRaises(HTTPNotFound):
            block(request)

    def test_independant_block(self):
        from cms_prototype.views.block import block

        request = testing.DummyRequest(matchdict={'block': self.block_id})
        response = block(request)

        self.assertEquals(response.status_code, 200)

    def test_table_block(self):
        from cms_prototype.views.block import block

        t = MongoTable(database=self.db.name, collection='block', columns=[MongoColumn(field='name')])
        t.save()

        request = testing.DummyRequest(matchdict={'block': t.id})
        response = block(request)

        self.assertEquals(response.status_code, 200)

        print response
