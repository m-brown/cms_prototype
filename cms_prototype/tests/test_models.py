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
        ld.layout.layout.append(Layout())
        ld.save()

        self.assertEqual(len(ld._layouts), 1)
        self.assertEqual(self.db.layout_doc.find().count(), 1)
        self.assertEqual(self.db.layout.find().count(), 0)

    def test_add_child_block(self):
        ld = LayoutDoc()
        l = LayoutDoc()
        b = Block(name='test')
        b.save()
        l.add(b)

        ld.add(l)
        ld.save()

        self.assertEqual(len(ld._layouts), 1)
        self.assertEqual(self.db.layout_doc.find().count(), 1)
        self.assertEqual(self.db.layout.find().count(), 0)

    def test_remove_block(self):
        ld = LayoutDoc()
        b = Block(name='test')
        b.save()

        ld.add(b)
        ld.save()

        self.assertEqual(len(ld._blocks), 1)

        ld.remove(b)
        ld.save()
        self.assertEqual(len(ld._blocks), 0)

    def test_remove_illegal(self):
        ld = LayoutDoc()
        b = Block(name='test')
        b.save()

        ld.add(b)
        ld.save()
        with self.assertRaises(Exception):
            ld.remove('test')

    def test_remove_not_present(self):
        ld = LayoutDoc()
        b = Block(name='test')
        b.save()

        ld.save()
        with self.assertRaises(Exception):
            ld.remove(b)
