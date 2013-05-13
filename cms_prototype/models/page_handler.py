from pyramid.renderers import render


class PageHandler:
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

    def __init__(self, page, inferred, get, post):
        self.page = page
        self.params = process_params(inferred, get, post)

    def pre_block_process(self):
        """
            Code to run before blocks are processed
        """
        #assume that the child class will not call super so put no code here
        return

    def block_process(self):
        if hasattr(self.page.layout, 'items'):
            for block in self.page.layout.items:
                if hasattr(block, 'process'):
                    block.process(self.params)
                if hasattr(block, 'populate'):
                    block.populate(self.params)

    def post_block_process(self):
        """
            Code to be run after blocks are processed
        """
        return

    def render(self):
        renderer = self.meta.get('renderer')
        args = {}
        args['page'] = self.page.to_mongo()

        if self.page.layout:
            args['layout'] = self.page.layout.render()
        else:
            args['layout'] = ''

        return render(renderer, args)


def process_params(inferred, get, post):
    return dict(get.items() + post.items() + inferred.items())
