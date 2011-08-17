""" """
import unittest
import colander
from colander.tests import TestMapping, TestSequence

    
class TestMemphisMapping(TestMapping):

    def _makeOne(self, *arg, **kw):
        from memphis.config.schema import Mapping
        return Mapping(*arg, **kw)

    def test_schema_mapping_flatten_without_name(self):
        node = colander.SchemaNode(
            self._makeOne(),
            
            colander.SchemaNode(
                colander.Int(),
                name = 'a'),

            colander.SchemaNode(
                colander.Int(),
                name = 'b'),
            )

        result = node.flatten({'a': 1, 'b':2})
        self.assertEqual(result, {'a': 1, 'b': 2})

    def test_schema_mapping_unflatten_without_name(self):
        node = colander.SchemaNode(
            self._makeOne(),
            
            colander.SchemaNode(
                self._makeOne(),

                colander.SchemaNode(
                    colander.Int(),
                    name = 'a'),
                
                colander.SchemaNode(
                    colander.Int(),
                    name = 'b'),
                
                name = 'node',
                ),
            )

        result = node.unflatten({'node.a': 1, 'node.b': 2})
        self.assertEqual(result, {'node': {'a': 1, 'b': 2}})

    def test_schema_mapping_unflatten_non_existing(self):
        node = colander.SchemaNode(
            self._makeOne(),
            
            colander.SchemaNode(
                self._makeOne(),
                colander.SchemaNode(colander.Int(), name = 'a'),
                colander.SchemaNode(colander.Int(), name = 'b'),
                name = 'node',
                )
            )

        result = node.unflatten({'node.a': 1, 'node.b': 2, 'node.c': 3})
        self.assertEqual(result, {'node': {'a': 1, 'b': 2}})


class TestMemphisSequence(TestSequence):

    def _makeOne(self, **kw):
        from memphis.config.schema import Sequence
        return Sequence(**kw)

    def test_schema_sequence_flatten(self):
        node = colander.SchemaNode(
            self._makeOne(),
            colander.SchemaNode(colander.Int()),
            name = 'node')

        result = node.flatten([1, 2])
        self.assertEqual(result, {'node.0': 1, 'node.1': 2})
