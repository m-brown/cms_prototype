from mongoengine import StringField

from cms_prototype.models.base import VersionedDocument

class Block(VersionedDocument):
    name        = StringField()
    meta        = {'allow_inheritance': True}

    def render(self, **kwargs):
        args = {k: v for k, v in self.to_mongo().iteritems() if k[0] != '_'}

        renderer = self._meta.get('renderer')
        if 'renderer' in kwargs:
            renderer = kwargs.pop('renderer')

        args.update(kwargs)

        if not renderer:
            raise Exception('No renderer found')

        return render(renderer, args)