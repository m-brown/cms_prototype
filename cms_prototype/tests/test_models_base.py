from mongoengine import StringField, IntField, EmbeddedDocument, EmbeddedDocumentField
from cms_prototype.models.base import VersionedDocument
from cms_prototype.tests.common import TestCase
from cms_prototype.models.site import Layout
from cms_prototype.models.blocks.block import Block


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

class SwitchableTypeFieldTestCase(TestCase):

    def test_basic_operation(self):
        from cms_prototype.models.base import SwitchableTypeField

        field = SwitchableTypeField((StringField(), IntField()))

        self.assertEqual('test', field.to_python('test'))
        self.assertEqual(0, field.to_python(0))

        field.validate(0)
        field.validate('test')

        with self.assertRaises(Exception):
            field.validate({})
