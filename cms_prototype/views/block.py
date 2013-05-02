from cms_prototype.models.blocks.block import Block

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='block')
def block(request):
    b = Block.objects(id=request.matchdict['block']).first()

    if not b:
        raise HTTPNotFound()
    else:
        return Response(b.render())
