""" Base handler class which controls the code side of each page load.
    Custom pages should inherit from this and override preload and postload.
"""
class PageHandler:
    def __init__(self, page):
        self.page = page

    """
        Code to run before blocks are processed
    """
    def preload(self):
        return

    """
        Code to be run after blocks are processed
    """
    def postload(self):
        return

    def render(self):
        return
