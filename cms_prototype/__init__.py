from pyramid.config import Configurator


def main(global_config='', **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if settings:
        config = Configurator(settings=settings)
    else:
        config = Configurator()
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('page', '/{site_unquie_name}/{url}')
    config.scan()
    return config.make_wsgi_app()
