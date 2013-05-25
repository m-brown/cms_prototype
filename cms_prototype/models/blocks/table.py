from mongoengine import EmbeddedDocument, EmbeddedDocumentField, ReferenceField, StringField, DictField, ListField, MapField
from cms_prototype.models.blocks.block import Block


class MongoColumn(EmbeddedDocument):
    field = StringField(required=True)
    display = StringField()


class MongoEngineTable(Block):
    mongoengine_class = StringField(required=True)
    columns = ListField(EmbeddedDocumentField(MongoColumn))
    spec = MapField(field=StringField())
    sort = DictField()

    meta = {'renderer': '/blocks/table.jade'}

    def render(self, **kwargs):
        if not hasattr(self, 'data'):
            self.populate({})
        args = {'data': self.data}
        args.update(kwargs)
        return super(MongoEngineTable, self).render(**args)

    def populate(self, request):
        sort = []
        for key, value in self.sort.iteritems():
            sort.append(('-' if value < 0 else '') + key)

        fields = {}
        for col in self.columns:
            fields[col.field] = 1

        mod, cls = self.mongoengine_class.split(':')
        mod = __import__(mod, globals(), locals(), [cls], -1)
        cls = getattr(mod, cls)

        spec = self.mapfield_to_dict(self.spec, request.PARAMS) if self.spec else {}

        objs = cls.objects(**spec).order_by(*sort)
        self.data = []
        for row in objs:
            r = {}
            for col in self.columns:
                r[col.field] = Block.get_dotted_value_from_object(row, col.field)
            self.data.append(r)
