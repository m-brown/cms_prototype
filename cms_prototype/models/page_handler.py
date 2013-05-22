from pyramid.renderers import render
from cms_prototype.models.blocks.form import Form


class PageHandler(object):
    """ Base handler class which controls the code side of each page load.
    Custom pages should inherit from this and override preload and postload.

    There are 5 steps once we have identified which page this is:
    1. Load initial data (__init__)
    2. Allow any code to exectute before blocks are processed (pre_block_process)
    3. Process blocks
    4. Allow any code to execture after blocks are processed (post_block_process)
    5. Render
"""

    meta = {'renderer': '/page.jade'}

    def __init__(self, request):
        self.request = request

    def pre_block_process(self):
        """
            Code to run before blocks are processed
        """
        #assume that the child class will not call super so put no code here
        return

    def block_process(self):
        if hasattr(self.request.url.page.layout, 'items'):
            for block in self.request.url.page.layout.items:
                if isinstance(block, Form) and self.request.POST:
                    block.post(self.request)
                if hasattr(block, 'process'):
                    block.process(self.request)
                if hasattr(block, 'populate'):
                    block.populate(self.request)

    def post_block_process(self):
        """
            Code to be run after blocks are processed
        """
        return

    def render(self):
        renderer = self.meta.get('renderer')
        args = {}
        args['page'] = self.request.url.page.to_mongo()

        if self.request.url.page.layout:
            args['layout'] = self.request.url.page.layout.render()
        else:
            args['layout'] = ''

        return render(renderer, args)
