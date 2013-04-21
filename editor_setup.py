from cms_prototype.models.site import Site, Page

s = Site(name='editor', unique_name='_editor')
s.save()


#site not found
p = Page(name='Site not found', body='<h1>Site not found</h1>')
