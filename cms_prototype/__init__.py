from pyramid.config import Configurator
from mongoengine import connect
import os


def main(global_config='', **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if settings:
        config = Configurator(settings=settings)
    else:
        config = Configurator()

    connect('cms', host=os.getenv('DB_HOST', 'localhost'))

    config.include('pyjade.ext.pyramid')

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('block', '/{site_unique_name}/_block/{block}')
    config.add_route('page', '/{site_unique_name}/{url}')

    config.scan('cms_prototype.views.page')

    return config.make_wsgi_app()
