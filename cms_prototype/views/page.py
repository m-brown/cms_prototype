from collections import namedtuple
from cms_prototype.models.site import Site, Url
from cms_prototype.models.page_handler import PageHandler
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='page')
def page(request, editor=False, editor_page=False):
    if editor_page:
        site = Site.objects(unique_name='_editor').first()
    else:
        site = Site.objects(unique_name=request.matchdict['site_unique_name']).first()
    if not site:
        raise HTTPFound(location='/%s/_editor/notfound?site_unique_name=%s' % (request.matchdict['site_unique_name'], request.matchdict['site_unique_name']))

    url = Url.objects(site=site.id, url=request.matchdict.get('url', '')).first()
    if editor and not url:
        raise HTTPFound(location='/%s/_editor/page?url=%s' % (request.matchdict['site_unique_name'], request.matchdict['url']))
    if not url:
        raise HTTPNotFound()

    #we still need the true site even if we loaded the _editor
    if editor_page:
        site = Site.objects(unique_name=request.matchdict['site_unique_name']).first()

    #attach bespoke objects to request
    request.cms = namedtuple('cms', ['page', 'site', 'url', 'is_editable'])
    request.cms.page = url.page
    request.cms.site = site
    request.cms.url = url
    request.cms.is_editable = editor
    request.PARAMS = dict(request.GET.items())  #TODO - add infered

    if url.page.handler_module:
        mod = __import__(url.page.handler_module, globals(), locals(), [url.page.handler_class], -1)
        HandlerClass = getattr(mod, url.page.handler_class)
        handler = HandlerClass(request=request)
    else:
        handler = PageHandler(request=request)

    handler.pre_block_process()
    handler.block_process()
    handler.post_block_process()
    return Response(handler.render())


@view_config(route_name='editor')
def editor(request):
    site = Site.objects(unique_name='_editor').first()
    url = Url.objects(site=site.id, url=request.matchdict.get('url', '')).first()

    if not url:
        return page(request, True, False)
    else:
        return page(request, False, True)


@view_config(route_name='site_nopage')
def site_nopage(request, editor=False):
    request.matchdict['url'] = 'index.html'
    return page(request, editor)
