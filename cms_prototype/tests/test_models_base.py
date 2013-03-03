from mongoengine import StringField, EmbeddedDocument, EmbeddedDocumentField
from cms_prototype.models.base import VersionedDocument
from cms_prototype.tests.common import TestCase
from cms_prototype.models.site import Layout, Block


class SomeTestDocument(VersionedDocument):
    some_key = StringField(max_length=50)
    meta = {'allow_inheritance': True}


class SomeTestInherited(SomeTestDocument):
    some_other_key = StringField()


class CompoundKey(EmbeddedDocument):
    a = StringField(required=True)
    b = StringField(required=True)


class Compound(VersionedDocument):
    key = EmbeddedDocumentField(CompoundKey, primary_key=True)


class VersionedDocumentTestCase(TestCase):
    def setUp(self):
        super(VersionedDocumentTestCase, self).setUp()
        self.db = SomeTestDocument._get_collection().database
        self.db.some_test_document.remove()
        self.db.versioned_some_test_document.remove()

    def test_base_fields(self):
        test_doc = SomeTestDocument(some_key='test')

        self.assertEquals(test_doc.id, None)

        test_doc.save()

        self.assertNotEquals(test_doc.id, None)
        self.assertNotEquals(test_doc._rev, None)
        self.assertNotEquals(test_doc._ts, None)
        self.assertEquals(test_doc._parent, None)

    def test_parent_history(self):
        test_doc = SomeTestDocument(some_key='test')
        test_doc.save()
        previous_rev = test_doc._rev
        test_doc.save()
        self.assertNotEquals(test_doc._rev, previous_rev)
        self.assertEquals(test_doc._parent, previous_rev)

    def test_single_revision(self):
        test_doc = SomeTestDocument(some_key='test value')
        test_doc.save()

        self.assertEqual(self.db.some_test_document.find().count(), 1)
        self.assertEqual(self.db.some_test_document.find({'_id': test_doc.id}).count(), 1)
        self.assertEqual(self.db.versioned_some_test_document.find().count(), 1)
        self.assertEqual(self.db.versioned_some_test_document.find({'_id.id': test_doc.id}).count(), 1)

    def test_double_revision(self):
        test_doc = SomeTestDocument(some_key='test value')
        test_doc.save()
        test_doc.some_key = 'some other value'
        test_doc.save()

        self.assertEqual(self.db.some_test_document.find().count(), 1)
        self.assertEqual(self.db.some_test_document.find({'_id': test_doc.id}).count(), 1)
        self.assertEqual(self.db.versioned_some_test_document.find().count(), 2)
        self.assertEqual(self.db.versioned_some_test_document.find({'_id.id': test_doc.id}).count(), 2)

    def test_two_documents(self):
        test_doc_1 = SomeTestDocument(some_key='foo')
        test_doc_2 = SomeTestDocument(some_key='bar')

        test_doc_1.save()
        test_doc_2.save()
        self.assertEqual(self.db.some_test_document.find().count(), 2)
        self.assertEqual(self.db.some_test_document.find({'_id': test_doc_1.id}).count(), 1)
        self.assertEqual(self.db.some_test_document.find({'_id': test_doc_2.id}).count(), 1)
        self.assertEqual(self.db.versioned_some_test_document.find().count(), 2)
        self.assertEqual(self.db.versioned_some_test_document.find({'_id.id': test_doc_1.id}).count(), 1)
        self.assertEqual(self.db.versioned_some_test_document.find({'_id.id': test_doc_2.id}).count(), 1)

        test_doc_1.save()
        test_doc_2.save()
        self.assertEqual(self.db.some_test_document.find().count(), 2)
        self.assertEqual(self.db.some_test_document.find({'_id': test_doc_1.id}).count(), 1)
        self.assertEqual(self.db.some_test_document.find({'_id': test_doc_2.id}).count(), 1)
        self.assertEqual(self.db.versioned_some_test_document.find().count(), 4)
        self.assertEqual(self.db.versioned_some_test_document.find({'_id.id': test_doc_1.id}).count(), 2)
        self.assertEqual(self.db.versioned_some_test_document.find({'_id.id': test_doc_2.id}).count(), 2)

    def test_inherited_document(self):
        test_doc = SomeTestDocument(some_key='foo')
        test_doc.save()
        inherted_doc = SomeTestInherited(some_key='foo', some_other_key='bar')
        inherted_doc.save()

        self.assertEqual(inherted_doc.some_key, 'foo')
        self.assertEqual(inherted_doc.some_other_key, 'bar')

        self.assertEqual(self.db.some_test_document.find().count(), 2)

    def test_compound_key(self):
        key = CompoundKey(a='foo', b='bar')
        compound_doc = Compound(key=key)
        compound_doc.save()

        self.assertEqual(self.db.compound.find().count(), 1)
        self.assertEqual(self.db.compound.find({'_id.a': 'foo'}).count(), 1)
        self.assertEqual(compound_doc.id.a, 'foo')
        self.assertEqual(compound_doc.id.b, 'bar')

class LayoutDoc(VersionedDocument):
    layout = EmbeddedDocumentField(Layout, dbref=True)

class Layout(TestCase):
    def setUp(self):
        super(VersionedDocumentTestCase, self).setUp()
        self.db = SomeTestDocument._get_collection().database
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
        b = Block(name='test')
        b.save()

        ld.add(b)
        ld.save()

        self.assertEqual(len(ld._blocks), 1)
        self.assertEqual(self.db.layout_doc.find().count(), 1)

    def test_add_layout(self):
        ld = LayoutDoc()
        l = Layout()

        ld.add(l)
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