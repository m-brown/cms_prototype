import os

from mongoengine import connect

from unittest import TestCase as _TestCase

class TestCase(_TestCase):

    def setUp(self):
        connect('cms', host=os.getenv('DB_HOST', 'localhost'))
