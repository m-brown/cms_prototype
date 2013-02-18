from datetime import datetime
from bson.objectid import ObjectId

from mongoengine import *
from mongoengine.base import TopLevelDocumentMetaclass

class VersionedDocumentMetaclass(TopLevelDocumentMetaclass):

    def __new__(cls, name, bases, attrs):
        super_new = super(VersionedDocumentMetaclass, cls).__new__

        attrs.update({
            '_rev':    ObjectIdField(required=True, default=ObjectId),
            '_parent': ObjectIdField(),
            '_ts':     DateTimeField(default=datetime.now),
        })

        new_cls = super_new(cls, name, bases, attrs)
        if name in ('VersionedDocument', 'PublishableDocument'):
            new_cls._is_base_cls =  True

        return new_cls

class VersionedDocument(Document):
     __metaclass__ = VersionedDocumentMetaclass

     def save(self, *args, **kwargs):
        Document.save.__doc__
        return super(VersionedDocument, self).save(*args, **kwargs)

class PublishableDocument(VersionedDocument):

    def publish(self, rev):
        raise NotImplementedError