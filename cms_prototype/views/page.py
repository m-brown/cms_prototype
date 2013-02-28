from cms_prototype.models.site import Site, Url, UrlKey

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

    return Response(url)