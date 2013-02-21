import os

from datetime import datetime
from bson.objectid import ObjectId

from mongoengine import *
from mongoengine.base import TopLevelDocumentMetaclass

class VersionedDocumentMetaclass(TopLevelDocumentMetaclass):

    def __new__(cls, name, bases, attrs):
        super_new = super(VersionedDocumentMetaclass, cls).__new__

        attrs.update({
            '_rev':         ObjectIdField(required=True, default=ObjectId),
            '_parent':      ObjectIdField(),
            '_ts':          DateTimeField(default=datetime.now)
        })

        new_cls = super_new(cls, name, bases, attrs)
        if name in ('VersionedDocument', 'PublishableDocument'):
            new_cls._is_base_cls =  True

        return new_cls

class VersionedDocument(Document):
     __metaclass__ = VersionedDocumentMetaclass

     def save(self, *args, **kwargs):
        Document.save.__doc__

        #generate a new revision
        if not self.id:
            self.id = ObjectId()
            self._parent = None
        else:
            self._parent = self._rev

        self._rev = ObjectId()
        self._ts = datetime.now()

        #save it in the versioning collection
        nv = self.to_mongo()
        nv['_id'] = {'id': self.id, 'rev': self._rev}

        db = self._collection.database
        db['versioned_'+self._meta['collection']].insert(nv, safe=True)

        return super(VersionedDocument, self).save(*args, **kwargs)

class PublishableDocument(VersionedDocument):

    def publish(self, rev):
        raise NotImplementedError
