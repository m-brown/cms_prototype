from cms_prototype.models.site import Site, Url
from cms_prototype.models.page_handler import PageHandler
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='page')
def page(request, editor=False):
    site = Site.objects(unique_name=request.matchdict['site_unique_name']).first()
    if not site:
        raise HTTPFound(location='/%s/_editor/notfound' % request.matchdict['site_unique_name'])

    url = Url.objects(key__site=site.id, key__url=request.matchdict.get('url', '')).first()
    if not url:
        raise HTTPNotFound()

    #attach bespoke objects to request
    request.site = site
    request.url = url
    request.PARAMS = dict(request.GET.items())#TODO - add infered

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
    url = Url.objects(key__site=site.id, key__url=request.matchdict.get('url', '')).first()

    if not url:
        return page(request, True)
    else:
        request.matchdict['site_unique_name'] = '_editor'
        return page(request, False)
