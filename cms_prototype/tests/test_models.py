from mongoengine import EmbeddedDocumentField
from cms_prototype.models.base import VersionedDocument
from cms_prototype.tests.common import TestCase
from cms_prototype.models.site import Layout, Block


class LayoutDoc(VersionedDocument):
    layout = EmbeddedDocumentField(Layout)


class LayoutTestCase(TestCase):

    def setUp(self):
        super(LayoutTestCase, self).setUp()

        self.db = LayoutDoc._get_collection().database
        self.db.layout_doc.remove()
        self.db.versioned_layout_doc.remove()
        self.db.block.remove()
        self.db.versioned_block.remove()

    def test_empty_layout(self):
        ld = LayoutDoc()
        ld.save()

        self.assertEqual(self.db.layout_doc.find().count(), 1)
        self.assertEqual(self.db.layout_doc.find({'_id': ld.id}).count(), 1)

    def test_add_illegal(self):
        ld = LayoutDoc()

        with self.assertRaises(Exception):
            ld.add('test')

    def test_add_block(self):
        ld = LayoutDoc()
        ld.layout = Layout()

        b = Block(name='test')
        b.save()

        ld.layout.items.append(b)
        ld.save()

        layout = self.db.layout_doc.find_one()
        self.assertEqual(len(layout['layout']['items']), 1)
        self.assertEqual(layout['layout']['items'][0]['_cls'], 'Block')
        self.assertEqual(self.db.layout_doc.find().count(), 1)

    def test_add_layout(self):
        ld = LayoutDoc()
        ld.layout = Layout()
        ld.layout.items.append(Layout())
        ld.save()

        self.assertEqual(len(ld.layout.items), 1)
        self.assertEqual(self.db.layout_doc.find().count(), 1)
        self.assertEqual(self.db.layout.find().count(), 0)

    def test_add_child_block(self):
        ld = LayoutDoc()
        ld.layout = Layout()
        l = Layout()
        b = Block(name='test')
        b.save()
        l.items.append(b)
        ld.layout.items.append(l)

        ld.save()

        self.assertEqual(len(ld.layout.items), 1)
        self.assertEqual(self.db.layout_doc.find().count(), 1)
        self.assertEqual(self.db.layout.find().count(), 0)

    def test_remove_block(self):
        ld = LayoutDoc()
        ld.layout = Layout()
        b = Block(name='test')
        b.save()

        ld.layout.items.append(b)
        ld.save()

        self.assertEqual(len(ld.layout.items), 1)

        ld.layout.items.remove(b)
        ld.save()
        self.assertEqual(len(ld.layout.items), 0)

    def test_remove_illegal(self):
        ld = LayoutDoc()
        ld.layout = Layout()
        b = Block(name='test')
        b.save()

        ld.layout.items.append(b)
        ld.save()
        with self.assertRaises(Exception):
            ld.layout.items.remove('test')

    def test_remove_not_present(self):
        ld = LayoutDoc()
        ld.layout = Layout()
        b = Block(name='test')
        b.save()

        ld.save()
        with self.assertRaises(Exception):
            ld.layout.items.remove(b)
