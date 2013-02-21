import os
import pprint

from datetime import datetime
from bson.objectid import ObjectId

from mongoengine import *
from mongoengine.base import TopLevelDocumentMetaclass

class VersionedDocument(Document):
    my_metaclass = TopLevelDocumentMetaclass

    _rev    = ObjectIdField(required=True, default=ObjectId)
    _parent = ObjectIdField()
    _ts     = DateTimeField(default=datetime.now)
    _meta   = {'abstract': True}

    def save(self, *args, **kwargs):
        Document.save.__doc__

        #generate a new revision
        if not self.id:
            self.id = ObjectId()
            self._parent  = None

            # self._created is an internal attribute used by MongoEngine to determine
            # what to do when saving the document. When we assign a value to self.id
            # this attribute gets set to False. We want to reset it to True so ME will
            # do its usual business when saving this new document.
            self._created = True
        else:
            self._parent = self._rev

        self._ts = datetime.now()
        self._rev = ObjectId()

        #save it in the versioning collection
        nv = self.to_mongo()
        nv['_id'] = {'id': self.id, 'rev': self._rev}

        db = self._get_db()
        db['versioned_'+self._meta['collection']].insert(nv, safe=True)

        return super(VersionedDocument, self).save(*args, **kwargs)

class PublishableDocument(VersionedDocument):

    def publish(self, rev):
        raise NotImplementedError
