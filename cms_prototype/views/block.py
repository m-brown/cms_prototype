from cms_prototype.models.site import Block

from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='block')
def block(request):
    db = Block._get_collection().database
    base = db.block.find(query={id: request.matchdict['block']}).first()
    return Response()
