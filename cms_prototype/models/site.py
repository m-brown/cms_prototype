from mongoengine import EmbeddedDocumentField, ReferenceField, StringField, DictField
from mongoengine import EmbeddedDocument
from cms_prototype.models.base import VersionedDocument


class Block(VersionedDocument):
    name        = StringField()
    _meta       = {'abstract': True}

class Page(VersionedDocument):
    handler     = StringField()
    parameters  = DictField()
    body        = StringField()


class Site(VersionedDocument):
    name        = StringField()
    unique_name = StringField()
    header      = ReferenceField(Block, dbref=True)
    footer      = ReferenceField(Block, dbref=True)


class UrlKey(EmbeddedDocument):
    site        = ReferenceField('Site', dbref=False)
    url         = StringField()


class Url(VersionedDocument):
    key         = EmbeddedDocumentField('UrlKey', primary_key=True)
    page        = ReferenceField(Page, dbref=True)

class Layout(EmbeddedDocument):
    html_id     = StringField()
    html_class  = StringField()
    _layouts    = DictField()
    _blocks     = DictField()

    def add(self, obj):
        nextPos = len(_layouts) + len(_blocks)
        if issubclass(type(obj), Layout):
            _layouts[nextPos] = obj
        elif issubclass(type(obj), Block):
            _blocks[nextPos] = obj
        else:
            raise Exception('Can only add Blocks or other Layouts to a Layout')

    def remove(self, obj):
        if issubclass(type(obj), Layout):
            for layout in _layouts:
                if _layouts[layout] == obj:
                    del _layouts[layout]
        elif issubclass(type(obj), Block):
            for block in _blocks:
                if _blocks[block] == obj:
                    del _blocks[block]
        else:
            raise Exception('Can only remove Blocks or Layouts')

    def save(self, *args, **kwargs):
        Document.save.__doc__

        for i in range(len(_layouts)+len(_blocks)):
            if i not in _layouts or i not in _blocks:
                raise Exception('Missing possition in layout')

        return super(Layout, self).save(*args, **kwargs)