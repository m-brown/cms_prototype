from unittest import TestCase
from collections import namedtuple
from cms_prototype.models.blocks.block import Block


class BlockFunctions(TestCase):
    def test_dotted_single_deepth(self):
        obj = namedtuple('foo', ['bar'])
        obj.bar = 'buz'
        val = 'bar'
        self.assertEqual(Block.get_dotted_value_from_object(obj, val), 'buz')

    def test_dotted_double_deepth(self):
        obj = namedtuple('foo', ['bar'])
        obj.bar = namedtuple('bar', ['buz'])
        obj.bar.buz = 'a'
        val = 'bar.buz'
        self.assertEqual(Block.get_dotted_value_from_object(obj, val), 'a')
