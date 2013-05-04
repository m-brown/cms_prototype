from mongoengine import BooleanField, IntField, ListField, StringField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField
from cms_prototype.models.blocks.block import Block


class Input(EmbeddedDocument):

    type  = StringField(required=True, default='text')
    name  = StringField(required=True)
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

    def process(self, post):
        try:
            mod, cls = self.mongo_object_class.split(':')
            module = __import__(mod, globals, locals, [cls], -1)
            MO_object = getattr(module, cls)
        except Exception, e:
            raise Exception("Cannot handle the mongoengine form: cannot find the class {0} in the module {1}.".format(mod, cls))

        if self.type == 'Update' and not 'id' in post:
            raise Exception("No Object ID in POST.")
        elif 'id' in post:
            o = MO_object.objects.get(id=post['id'])
        else:
            o = MO_object()

        for field in self.fields:
            if field.name in post:
                o[field.name] = post[field.name]

        o.save()
