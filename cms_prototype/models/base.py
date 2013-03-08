import os
import pprint

from datetime import datetime
from bson.objectid import ObjectId

from mongoengine import *
from mongoengine.base import TopLevelDocumentMetaclass
from mongoengine.base import ComplexBaseField

class VersionedDocument(Document):
    my_metaclass = TopLevelDocumentMetaclass

    _rev    = ObjectIdField(required=True)
    _parent = ObjectIdField()
    _ts     = DateTimeField(default=datetime.now)
    _meta   = {'abstract': True}

    def save(self, *args, **kwargs):
        Document.save.__doc__

        #generate a new revision
        if not self.id:
            self.id = ObjectId()
            # self._created is an internal attribute used by MongoEngine to determine
            # what to do when saving the document. When we assign a value to self.id
            # this attribute gets set to False. We want to reset it to True so ME will
            # do its usual business when saving this new document.
            self._created = True
            self._parent = None
        else:
            self._parent = self._rev

        self._ts = datetime.now()
        self._rev = ObjectId()

        #save it in the versioning collection
        nv = self.to_mongo()
        if issubclass(type(self.id), EmbeddedDocument):
            nv['_id'] = {'id': self.id.to_mongo(), 'rev': self._rev}
        else:
            nv['_id'] = {'id': self.id, 'rev': self._rev}

        db = self._get_db()
        db['versioned_'+self._meta['collection']].insert(nv, safe=True)

        return super(VersionedDocument, self).save(*args, **kwargs)

# FIXME: There must be a nicer way around this than doing this?
# Due to our hackery extending the base document our class we don't end up with a
# _fields attribute on the class or the _db_field_map or _reverse_db_field_map. To
# get around this we add these in manually now. The field names also are not being
# set so we need to do that as well.
_vd = VersionedDocument
_vd._fields = {
    '_rev':    VersionedDocument._rev,
    '_parent': VersionedDocument._parent,
    '_ts':     VersionedDocument._ts
}
_vd._rev.name    = _vd._rev.db_field    = '_rev'
_vd._parent.name = _vd._parent.db_field = '_parent'
_vd._ts.name     = _vd._ts.db_field     = '_ts'
_vd._db_field_map = {'_parent': '_parent', '_rev': '_rev', '_ts': '_ts'}
_vd._reverse_db_field_map = _vd._db_field_map
del _vd

class PublishableDocument(VersionedDocument):

    def publish(self, rev):
        raise NotImplementedError

class SwitchableTypeField(ComplexBaseField):

    def __init__(self, fields, **kwargs):
        self.fields = fields
        super(SwitchableTypeField, self).__init__(**kwargs)

    def to_python(self, value):
        for field in self.fields:
            try:
                return field.to_python(value)
            except:
                pass

        return value

    def validate(self, value):
        """
        Check the values
        """
        good_val = False
        for field in self.fields:
            try:
                field.validate(value)
            except:
                continue

            good_val = True
            break

        if not good_val:
            self.error('Value is not valid for any of the supported fields')
