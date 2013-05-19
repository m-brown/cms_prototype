from pyramid.httpexceptions import HTTPFound
from mongoengine import BooleanField, IntField, ListField, StringField, MapField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField
from cms_prototype.models.blocks.block import Block


class Input(EmbeddedDocument):
    html_id = StringField()
    html_class = StringField()
    type = StringField(required=True, default='text')
    name = StringField(required=True)
    label = StringField()

    meta = {'allow_inheritance': True}


class Checkbox(Input):

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'checkbox'
        super(Checkbox, self).__init__(*args, **kwargs)

    checked = BooleanField(default=False)


class Form(Block):
    action = StringField(default='', required=False)
    method = StringField(default='POST', regex=r'(GET|POST)', required=True)
    fields = ListField(EmbeddedDocumentField(Input))
    next_page = StringField()

    meta = {'renderer': '/blocks/form.jade'}


class MongoEngineForm(Form):
    mongo_object_class = StringField(required=True)
    type = StringField(default="Upsert", regex=r'(Upsert|Update)')
    identity = MapField(field=StringField())

    def _get_mongoengine_class(self):
        try:
            mod, cls = self.mongo_object_class.split(':')
            module = __import__(mod, globals, locals, [cls], -1)
            return getattr(module, cls)
        except Exception, e:
            raise Exception("Cannot handle the mongoengine form: cannot find the class {0} in the module {1}.".format(mod, cls))

    def _get_identifier(self, parameters):
        if not self.identity or len(self.identity) == 0:
            raise Exception('Cannot populate form: no identifier was set')
        id = {}
        for prop in self.identity:
            if not prop in parameters:
                raise Exception('Cannot populate form: missing parameter - %', prop)
            id[self.identity[prop]] = parameters[prop]
        return id

    def to_mongo(self):
        o = super(MongoEngineForm, self).to_mongo()
        for pos, f in enumerate(self.fields):
            if 'value' in f:
                o['fields'][pos]['value'] = f.value
        return o

    def populate(self, parameters):
        MO_class = self._get_mongoengine_class()
        try:
            id = self._get_identifier(parameters)
        except Exception, e:
            return
        o = MO_class.objects.get(**id)

        for f in self.fields:
            if f.type != 'submit':
                f.value = o[f.name]

    def post(self, parameters):
        MO_class = self._get_mongoengine_class()
        try:
            id = self._get_identifier(parameters)
            o = MO_class.objects.get(**id)
        except Exception, e:
            if self.type == 'Update':
                raise e
            else:
                o = MO_class()

        for field in self.fields:
            if field.type != 'submit':
                if field.name in parameters:
                    o[field.name] = parameters[field.name]
                    field.value = parameters[field.name]
                else:
                    field.value = o[field.name]

        o.save()
        if self.next_page:
            raise HTTPFound(location=self.next_page)
