from mongoengine import EmbeddedDocument, EmbeddedDocumentField, ReferenceField, StringField, DictField, ListField, MapField
from cms_prototype.models.blocks.block import Block


class MongoColumn(EmbeddedDocument):
    field = StringField(required=True)
    display = StringField()


class MongoEngineTable(Block):
    database = StringField(required=True)
    collection = StringField(required=True)
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

    def populate(self, parameters):
        sort = []
        for key, value in self.sort.iteritems():
            sort.append((key, value))

        fields = {}
        for col in self.columns:
            fields[col.field] = 1

        spec = self.mapfield_to_dict(self.spec, parameters) if self.spec else {}
        cursor = MongoEngineTable._get_collection().database[self.collection].find(spec, fields=fields, sort=sort)
        self.data = []
        for row in cursor:
            r = {}
            for col in self.columns:
                if not col.field in row:
                    raise AttributeError('The row has not attribute "' + col.field + '"')
                r[col.field] = row[col.field]
            self.data.append(r)
