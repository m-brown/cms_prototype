from cms_prototype.models.site import Site, Url, UrlKey

def page(request):
    site = Site.objects(unique_name=request.unique_name)
    urlKey = UrlKey(site=site, url=request.url)
    url = Url.objects(key=urlKey)
    return url