import colander
import unittest

from colander.tests import TestMapping, TestSequence, TestSchemaNode


class TestptahMapping(TestMapping):

    def _makeOne(self, *arg, **kw):
        from ptah.config.schema import Mapping
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

        result = node.flatten({'a': 1, 'b': 2})
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


class TestptahSequence(TestSequence):

    def _makeOne(self, **kw):
        from ptah.config.schema import Sequence
        return Sequence(**kw)

    def test_schema_sequence_flatten(self):
        node = colander.SchemaNode(
            self._makeOne(),
            colander.SchemaNode(colander.Int()),
            name = 'node')

        result = node.flatten([1, 2])
        self.assertEqual(result, {'node.0': 1, 'node.1': 2})


class TestptahString(unittest.TestCase):

    def test_schema_str(self):
        from ptah.config.schema import Str

        typ = Str()

        self.assertEqual(typ.encoding, 'utf-8')


class TestptahSchemaNode(unittest.TestCase):

    def _makeOne(self, *arg, **kw):
        from ptah.config.schema import SchemaNode
        return SchemaNode(*arg, **kw)

    def test_schema_node_deserialize(self):
        from ptah.config.schema import Required

        node = self._makeOne(
            colander.Int(),
            name = 'node')

        self.assertEqual(node.deserialize('1'), 1)

        self.assertRaises(
            Required, node.deserialize)

        node = self._makeOne(
            colander.Int(),
            name = 'node',
            default = 100)

        self.assertEqual(node.deserialize(), 100)

    def test_schema_node_deserialize_common(self):
        def validator(node, val):
            if val == 10:
                raise colander.Invalid('Error')

        node = self._makeOne(
            colander.Int(),
            name = 'node',
            validator = validator)

        self.assertRaises(
            colander.Invalid, node.deserialize, '10')

        node = self._makeOne(
            colander.Int(),
            name = 'node',
            preparer = lambda x: x * 2,
            default = 100)

        self.assertEqual(node.deserialize(), 200)

    def test_schema_node_deserialize_str(self):
        from ptah.config.schema import Required

        node = self._makeOne(
            colander.Str(),
            name = 'node',
            default = 'default')

        self.assertEqual(node.deserialize('test'), 'test')
        self.assertEqual(node.deserialize(''), 'default')
        self.assertEqual(node.deserialize(), 'default')

        node = self._makeOne(
            colander.Str(),
            name = 'node',
            required = True,
            default = 'default')

        self.assertEqual(node.deserialize('test'), 'test')
        self.assertRaises(Required, node.deserialize, '')
        self.assertRaises(Required, node.deserialize)


class TestRequiredWithDependency(unittest.TestCase):

    def test_schema_required_validator(self):
        from ptah import config
        from ptah.config.schema import Required

        v = config.RequiredWithDependency(
            'field', 'depends', 'depvalue', 'default')

        self.assertEqual(v(None, {}), None)
        self.assertEqual(v(None, {'depends': 'sothing diff'}), None)
        self.assertEqual(v(None,
                           {'field': 'val', 'depends': 'sothing diff'}), None)

        self.assertRaises(
            Required,
            v, {'field':
                colander.SchemaNode(colander.Str(), name='field')},
            {'depends': 'depvalue'})

        v = config.RequiredWithDependency('field', 'depends')
        self.assertRaises(
            Required,
            v, {'field':
                colander.SchemaNode(colander.Str(), name='field')},
            {'depends': 'somthing diff'})

        self.assertEqual(
            v({'field':
               colander.SchemaNode(colander.Str(), name='field')},
              {'field': 'val', 'depends': 'somthing diff'}), None)
