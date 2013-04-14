from cms_prototype.models.site import Site, Url
from cms_prototype.models.page_handler import PageHandler
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='page')
def page(request):
    site = Site.objects(unique_name=request.matchdict['unique_name']).first()
    if not site:
        raise HTTPNotFound()

    url = Url.objects(key__site=site.id, key__url=request.matchdict.get('url', '')).first()
    if not url:
        raise HTTPNotFound()

    if url.page.handler_module:
        mod = __import__(url.page.handler_module, globals(), locals(), [url.page.handler_class], -1)
        HandlerClass = getattr(mod, url.page.handler_class)
        handler = HandlerClass(page=url.page)
    else:
        handler = PageHandler(page=url.page)

    handler.pre_block_process()
    handler.block_process()
    handler.post_block_process()
    return Response(handler.render())
