import os
from mongoengine import connect

from cms_prototype.models.site import Site, Page, Url, UrlKey
from cms_prototype.models.site import Layout
from cms_prototype.models.blocks.text import HTMLBlock
from cms_prototype.models.blocks.link import Link


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
link = Link(href='site', text='Create?')
link.save()
l.items.append(heading)
l.items.append(link)
p = Page(name='Site not found', layout=l)
p.save()

k = UrlKey(site=s, url='notfound.html')
url = Url(key=k, page=p)
url.save()
