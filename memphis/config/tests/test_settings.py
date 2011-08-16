""" """
import unittest
import colander
from memphis import config
from zope.interface.interface import InterfaceClass


class TestSettings(unittest.TestCase):

    def _init_memphis(self, settings={}, *args, **kw):
        config.begin()
        config.loadPackage('memphis.config')
        config.addPackage(self.__class__.__module__)
        config.commit()
        #config.initializeSettings(settings, None)

    def tearDown(self):
        config.cleanUp()

    def test_settings_register_errs(self):
        self.assertRaises(
            RuntimeError,
            config.registerSettings,
            'section',
            colander.SchemaNode(
                colander.Str(),
                name = 'node')
            )

    def test_settings_register_simple(self):
        node = config.SchemaNode(
                colander.Str(),
                name = 'node',
                default = 'test')

        group = config.registerSettings(
            'group1', node,
            title = 'Section title',
            description = 'Section description',
            )

        self.assertEqual(group.name, 'group1')
        self.assertEqual(group.title, 'Section title')
        self.assertEqual(group.description, 'Section description')
        self.assertEqual(len(group.schema.children), 0)
        self.assertTrue(isinstance(group.category, InterfaceClass))
        
        self._init_memphis()

        self.assertEqual(len(group.schema.children), 1)
        self.assertTrue(group.schema.children[0] is node)
        self.assertEqual(group.node, 'test')
        self.assertEqual(group['node'], 'test')
        self.assertRaises(
            AttributeError,
            group.__getattr__, 'unknown')
        self.assertRaises(
            KeyError,
            group.__getitem__, 'unknown')

        self.assertEqual(config.Settings._changed, None)

        group.node = 'test2'
        self.assertFalse(group.node == group['node'])

        group['node'] =  'test2'
        self.assertTrue('group1' in config.Settings._changed)
        self.assertTrue('node' in config.Settings._changed['group1'])

