from pyramid.renderers import render


""" Base handler class which controls the code side of each page load.
    Custom pages should inherit from this and override preload and postload.

    There are 5 steps once we have identified which page this is:
    1. Load initial data (__init__)
    2. Allow any code to exectute before blocks are processed (pre_block_process)
    3. Process blocks
    4. Allow any code to execture after blocks are processed (post_block_process)
    5. Render
"""
class PageHandler:
    meta = {'renderer': '/page.jade'}

    def __init__(self, page):
        self.page = page

    """
        Code to run before blocks are processed
    """
    def pre_block_process(self):
        #assume that the child class will not call super so put no code here
        return

    def block_process(self):
        #assume that the child class will not call super so put no code here
        return

    """
        Code to be run after blocks are processed
    """
    def post_block_process(self):
        return

    def render(self):
        renderer = self.meta.get('renderer')
        args = {}
        args['page'] = self.page.to_mongo()

        if self.page.layout:
            args['layout'] = self.page.layout.render()

        return render(renderer, args)
