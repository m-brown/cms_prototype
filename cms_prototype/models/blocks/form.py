from collections import namedtuple
from pyramid.httpexceptions import HTTPFound
from mongoengine import BooleanField, IntField, ListField, StringField, MapField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField
from mongoengine.queryset import DoesNotExist
from cms_prototype.models.blocks.block import Block, MissingParameter


class Input(EmbeddedDocument):
    name = StringField(required=True)
    type = StringField(required=True, default='text')
    label = StringField()
    default = StringField()

    html_id = StringField()
    html_class = StringField()

    meta = {'allow_inheritance': True}


class Checkbox(Input):
    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'checkbox'
        super(Checkbox, self).__init__(*args, **kwargs)

    checked = BooleanField(default=False)


class Select(Input):
    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'select'
        super(Select, self).__init__(*args, **kwargs)

    name_field = StringField(required=True)
    value_field = StringField(required=True)
    identity = MapField(field=StringField())
    sort_by = StringField()


class Form(Block):
    action = StringField(default='', required=False)
    method = StringField(default='POST', regex=r'(GET|POST)', required=True)
    fields = ListField(EmbeddedDocumentField(Input))
    next_page = StringField()

    meta = {'renderer': '/blocks/form.jade'}

    def serialize(self, include_new_params=True):
        """
        Similar to to_mongo() but includes the additional
        parameters created at run time. Primarily used for
        rendering
        """
        o = self.to_mongo()
        if include_new_params:
            for pos, f in enumerate(self.fields):
                if 'value' in f:
                    o['fields'][pos]['value'] = f.value
                if 'options' in f:
                    o['fields'][pos]['options'] = []
                    for opt in f.options:
                        o['fields'][pos]['options'].append({'name': opt.name, 'value': opt.value})
        return o


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

    def populate(self, request):
        MO_class = self._get_mongoengine_class()

        #process any fields first as we need to which values are acceptable
        for field in self.fields:
            if isinstance(field, Select):
                cls = getattr(MO_class, field.name).document_type
                try:
                    if len(field.identity):
                        id = Block.mapfield_to_dict(field.identity, request.PARAMS, request.cms)
                        objs = cls.objects.get(**id)
                    else:
                        objs = cls.objects.all()
                    field.options = []
                    for o in objs:
                        option = namedtuple('option', ['name', 'value'])
                        setattr(option, 'name', getattr(o, field.name_field))
                        setattr(option, 'value', getattr(o, field.value_field))
                        field.options.append(option)
                except DoesNotExist, e:
                    pass

        #populate values of the fields
        try:
            id = Block.mapfield_to_dict(self.identity, request.PARAMS, request.cms)
            o = MO_class.objects.get(**id)

            for f in self.fields:
                if f.type != 'submit':
                    f.value = o[f.name]
        except DoesNotExist:
            return
        except MissingParameter, e:
            for f in self.fields:
                if f.type != 'submit' and f.default:
                    v = Block.get_value(request, f.default)
                    if v:
                        f.value = v

    def post(self, request):
        MO_class = self._get_mongoengine_class()
        try:
            id = Block.mapfield_to_dict(self.identity, request.POST, request.cms)
            o = MO_class.objects.get(**id)
        except Exception, e:
            if self.type == 'Update':
                raise e
            else:
                o = MO_class()

        for field in self.fields:
            if field.type != 'submit':
                if field.name in request.POST:
                    o[field.name] = request.POST[field.name]
                    field.value = request.POST[field.name]
                else:
                    field.value = o[field.name]

        o.save()
        if self.next_page:
            raise HTTPFound(location=self.next_page)
