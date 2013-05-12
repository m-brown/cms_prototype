from mongoengine import BooleanField, IntField, ListField, StringField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField
from cms_prototype.models.blocks.block import Block


class Input(EmbeddedDocument):

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

    meta = {'renderer': '/blocks/form.jade'}


class MongoEngineForm(Form):
    mongo_object_class = StringField(required=True)
    type = StringField(default="Upsert", regex=r'(Upsert|Update)')
    identity = ListField(StringField())

    def _get_mongoengine_class(self):
        try:
            mod, cls = self.mongo_object_class.split(':')
            module = __import__(mod, globals, locals, [cls], -1)
            return getattr(module, cls)
        except Exception, e:
            raise Exception("Cannot handle the mongoengine form: cannot find the class {0} in the module {1}.".format(mod, cls))

    def to_mongo(self):
        o = super(MongoEngineForm, self).to_mongo()
        for pos, f in enumerate(self.fields):
            if 'value' in f:
                o['fields'][pos]['value'] = f.value
        return o

    def populate(self, parameters):
        if len(self.identity) == 1:
            if not self.identity[0] in parameters:
                raise Exception('Cannot populate form: missing parameter - %', prop)
            v = parameters[self.identity[0]]

            MO_object = self._get_mongoengine_class()
            o = MO_object.objects.get(id=v)

            for f in self.fields:
                f.value = o[f.name]

        if len(self.identity) > 1:
            id = {}
            for prop in self.identity:
                if not prop in parameters:
                    raise Exception('Cannot populate form: missing parameter - %', prop)
                id[prop] = parameters[prop]

            MO_object = self._get_mongoengine_class()
            o = MO_object.objects.get(**id)

            for f in self.fields:
                f.value = o[f.name]

    def process(self, post):
        MO_object = self._get_mongoengine_class()
        if self.type == 'Update' and not 'id' in post:
            raise Exception("No Object ID in POST.")
        elif 'id' in post:
            o = MO_object.objects.get(id=post['id'])
        else:
            o = MO_object()

        for field in self.fields:
            if field.name in post:
                o[field.name] = post[field.name]
                field.value = post[field.name]

        o.save()
