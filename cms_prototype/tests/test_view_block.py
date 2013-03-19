from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from cms_prototype.tests.common import TemplateTestCase
from cms_prototype.models.site import Block
from cms_prototype.models.table import MongoTable, MongoColumn
from cms_prototype.models.text import HTMLBlock
from bson.objectid import ObjectId


class BlockViewTest(TemplateTestCase):

    def setUp(self):
        super(BlockViewTest, self).setUp()

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

    def test_text_block(self):
        from cms_prototype.views.block import block

        html = HTMLBlock(text='Fun test time')
        html.save()

        request = testing.DummyRequest(matchdict={'block': html.id})
        response = block(request)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.body.strip(), 'Fun test time')
