from cms_prototype.models.site import Site, Url

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

def load_handler(handler):
    # do magic loading
    if not hasattr('pre_load', module):
        setattr('pre_load', None)


@view_config(route_name='page')
def page(request):
    site = Site.objects(unique_name=request.matchdict['unique_name']).first()
    if not site:
        raise HTTPNotFound()

    url = Url.objects(key__site=site.id, key__url=request.matchdict.get('url', '')).first()
    if not url:
        raise HTTPNotFound()

    handler = load_handler(url.page.handler) if url.page.handler else None

    if handler:
        handler.pre_load(request)

    # Do stuff

    if handler:
        handler.post_load(request, None)

    return Response(url)
