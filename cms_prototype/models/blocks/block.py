from mongoengine import StringField
from pyramid.renderers import render

from cms_prototype.models.base import VersionedDocument


class Block(VersionedDocument):
    name        = StringField()
    html_class  = StringField()
    html_id     = StringField()
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

    def mapfield_to_dict(self, mapfield, parameters):
        if not mapfield or len(mapfield) == 0:
            raise Exception('Cannot populate dict: no mapfield was given')
        d = {}
        for f in mapfield:
            if not f in parameters:
                raise Exception('Cannot populate dict: missing parameter - %s' % f)
            d[mapfield[f]] = parameters[f]
        return d

    @staticmethod
    def get_dotted_value_from_object(obj, val):
        parts = val.split('.')
        obj = getattr(obj, parts[0])
        if len(parts) == 1:
            return obj
        else:
            return Block.get_dotted_value_from_object(obj, val[val.index('.') + 1:])