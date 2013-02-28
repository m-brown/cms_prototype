from pyramid.config import Configurator

def main(global_config='', **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if settings:
        config = Configurator(settings=settings)
    else:
        config = Configurator()
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('page', '/{site_unique_name}/{url}')

    config.scan('cms_prototype.views.page')
    return config.make_wsgi_app()
