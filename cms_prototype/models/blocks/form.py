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
    type   = IntField(default=1)
    action = StringField(default='', required=False)
    method = StringField(default='POST', regex=r'(GET|POST)')
    fields = ListField(EmbeddedDocumentField(Input))

    meta = {'renderer': '/blocks/form.jade'}


class MongoEngineForm(Form):
    mongo_object_class = StringField(required=True)

    def process(self, post):
        mod, cls = self.mongo_object_class.split(':')
        mod = __import__(mod, globals, locals, [cls], -1)
        MO_object = getattr(mod, cls)

        if not MO_object:
            raise Exception("Cannot handle the mongoengine form: cannot find the class {0} in the module {1}.".format(class_module, class_name))

        if not 'id' in post:
            raise Exception("No Object ID in POST.")

        o = MO_object.objects.get(id=post['id'])

        for field in self.fields:
            if field.name in post:
                o[field.name] = post[field.name]
                print o[field.name]

        o.save()
