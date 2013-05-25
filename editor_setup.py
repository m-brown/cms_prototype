import os
from mongoengine import connect

from cms_prototype.models.site import Site, Page, Url
from cms_prototype.models.site import Layout
from cms_prototype.models.blocks.text import HTMLBlock
from cms_prototype.models.blocks.link import Link
from cms_prototype.models.blocks.form import MongoEngineForm, Input
from cms_prototype.models.blocks.table import MongoEngineTable, MongoColumn


connect('cms', host=os.getenv('DB_HOST', 'localhost'))
from cms_prototype.models.base import VersionedDocument
db = VersionedDocument._get_db()
db.connection.drop_database('cms')


s = Site(name='editor', unique_name='_editor')
s.save()


#site not found
l = Layout()
heading = HTMLBlock(text='<h1>Site not found!</h1>')
heading.save()
link = Link(href='create', text='Create?', html_class='btn btn-primary')
link.save()
l.items.append(heading)
l.items.append(link)
p = Page(name='Site not found', layout=l)
p.save()

url = Url(site=s, url='notfound', page=p)
url.save()


#create new site
f = MongoEngineForm(mongo_object_class='cms_prototype.models.site:Site',
                    identity={'unique_name': 'unique_name'},
                    next_page='pages')
f.fields.append(Input(name='name', label='Name'))
f.fields.append(Input(name='unique_name', label='Unique Name'))
f.fields.append(Input(name='submit', type='submit', html_class='btn'))
f.save()
l = Layout()
l.items.append(f)
p = Page(name='Create Site', layout=l)
p.save()

url = Url(site=s, url='create', page=p)
url.save()


#pages
t = MongoEngineTable(mongoengine_class='cms_prototype.models.site:Url',
                    columns=[MongoColumn(field='id.url', display='URL'),
                            MongoColumn(field='page.id', display='Page Type')],
                    spec={'site': '_id.site'})
t.save()

l = Layout()
l.items.append(t)
p = Page(name='URL List', layout=l)
p.save()

url = Url(site=s, url='pages', page=p)
url.save()
