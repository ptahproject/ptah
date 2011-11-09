import sys, os, time
import unittest, shutil, tempfile, colander
from zope.interface.registry import Components
from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import IObjectEvent

from ptah import config
from ptah.config.api import objectEventNotify
from ptah.config.settings import get_settings


class BaseTesting(unittest.TestCase):

    def _init_ptah(self, settings={}, *args, **kw):
        config.initialize(
            ('ptah.config', self.__class__.__module__),
            registry = Components('test'))

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)


class TestSettings(BaseTesting):

    def test_settings_group_uninitialized(self):
        node = config.SchemaNode(
                colander.Str(),
                name = 'node',
                default = 'test')

        group = config.register_settings(
            'group1', node,
            title = 'Section title',
            description = 'Section description',
            )

        self.assertEqual(group.get('node'), 'test')

    def test_settings_register_errs(self):
        self.assertRaises(
            RuntimeError,
            config.register_settings,
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

        group = config.register_settings(
            'group1', node,
            title = 'Section title',
            description = 'Section description',
            )

        self.assertEqual(group.name, 'group1')
        self.assertEqual(group.title, 'Section title')
        self.assertEqual(group.description, 'Section description')
        self.assertEqual(len(group.schema.children), 1)
        self.assertTrue(isinstance(group.category, InterfaceClass))

        self._init_ptah()

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

        group.node = 'test2'
        self.assertFalse(group.node == group['node'])

    def test_settings_group_validation(self):
        def validator(node, appstruct):
            raise colander.Invalid(node['node'], 'Error')

        node = config.SchemaNode(
                colander.Str(),
                name = 'node',
                default = 'test')

        group = config.register_settings(
            'group2', node, validator=validator)

        self._init_ptah()

        try:
            group.schema.deserialize({'group2.node': 'value'})
        except colander.Invalid, err:
            pass

        self.assertEqual(err.asdict(), {'group2.node': 'Error'})

    def test_settings_group_multiple_validation(self):
        def validator1(node, appstruct):
            raise colander.Invalid(node['node1'], 'Error1')
        def validator2(node, appstruct):
            raise colander.Invalid(node, 'Error2')

        node1 = config.SchemaNode(
                colander.Str(),
                name = 'node1',
                default = 'test')

        node2 = config.SchemaNode(
                colander.Str(),
                name = 'node2',
                default = 'test')

        group = config.register_settings(
            'group3', node1, node2, validator=(validator1, validator2))

        self._init_ptah()

        try:
            group.schema.deserialize({
                    'group3.node1': 'value',
                    'group3.node2': 'value'})
        except colander.Invalid, err:
            pass

        self.assertEqual(err.asdict(),
                         {'group3.group3': 'Error2', 'group3.node1': 'Error1'})

    def test_settings_export(self):
        node1 = config.SchemaNode(
                colander.Str(),
                name = 'node1',
                default = 'test')

        node2 = config.SchemaNode(
                colander.Str(),
                name = 'node2',
                default = 'test')

        group = config.register_settings('group4', node1, node2)

        self._init_ptah()

        settings = get_settings()

        # changed settings
        self.assertEqual(settings.export(), {})

        # default settings
        self.assertEqual(settings.export(default=True),
                         {'group4.node1': 'test', 'group4.node2': 'test'})

        # changed settings
        group['node2'] = 'changed'
        data = dict(settings.export())
        self.assertEqual(data, {'group4.node2': 'changed'})

    def _create_default_group(self):
        node1 = config.SchemaNode(
                colander.Str(),
                name = 'node1',
                default = 'default1')

        node2 = config.SchemaNode(
                colander.Int(),
                name = 'node2',
                default = 10)

        group = config.register_settings('group', node1, node2)
        self._init_ptah()

        return group

    def test_settings_load_rawdata(self):
        group = self._create_default_group()

        get_settings()._load({'group.node1': 'val1'})

        # new value
        self.assertEqual(group['node1'], 'val1')

        # default value
        self.assertEqual(group['node2'], 10)

    def test_settings_load_rawdata_and_change_defaults(self):
        group = self._create_default_group()

        # change defaults
        get_settings()._load({'group.node2': 30}, setdefaults=True)

        # new values
        self.assertEqual(group['node1'], 'default1')
        self.assertEqual(group['node2'], 30)

        self.assertEqual(group.schema['node1'].default, 'default1')
        self.assertEqual(group.schema['node2'].default, 30)

    def test_settings_load_rawdata_with_errors_in_rawdata(self):
        group = self._create_default_group()

        get_settings()._load({10: 'value'})
        self.assertEqual(dict(group), {'node1': 'default1', 'node2': 10})

    def test_settings_load_rawdata_with_errors_in_values(self):
        group = self._create_default_group()

        get_settings()._load({'group.node2': 'vadfw234lue'})
        self.assertEqual(dict(group), {'node1': 'default1', 'node2': 10})

    def test_settings_load_defaults_rawdata_with_errors_in_values(self):
        group = self._create_default_group()

        get_settings()._load({'group.node2': 'vadfw234lue'}, setdefaults=True)
        self.assertEqual(dict(group),
                         {'node1': 'default1', 'node2': 10})

    def test_settings_load_defaults_rawdata_with_errors_in_colander(self):
        node = config.SchemaNode(
            config.Sequence(), colander.SchemaNode(colander.Str()),
            name = 'node1',
            default = ())

        group = config.register_settings('group', node)
        self._init_ptah()

        self.assertRaises(
            KeyError, 
            get_settings()._load,
            {'group.node1.0': '1',
             'group.node1.3': '1'}, setdefaults=True)

    def test_settings_init_with_no_loader_with_defaults(self):
        group = self._create_default_group()

        get_settings().init({'group.node1': 'new-default',
                             'group.node2': 50})

        self.assertEqual(group['node1'], 'new-default')
        self.assertEqual(group['node2'], 50)

        self.assertEqual(group.schema['node1'].default, 'new-default')
        self.assertEqual(group.schema['node2'].default, 50)


class TestSettingsInitialization(BaseTesting):

    def setUp(self):
        config.cleanup_system()
        BaseTesting.setUp(self)
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        BaseTesting.tearDown(self)
        shutil.rmtree(self.dir)

    def test_settings_initialize_events(self):
        self._init_ptah()

        sm = config.registry

        events = []
        def h1(ev):
            events.append(ev)
        def h2(ev):
            events.append(ev)

        sm.registerHandler(h1, (config.SettingsInitializing,))
        sm.registerHandler(h2, (config.SettingsInitialized,))

        settings = get_settings()

        conf = object()
        config.initialize_settings({}, conf)

        self.assertTrue(isinstance(events[0], config.SettingsInitializing))
        self.assertTrue(isinstance(events[1], config.SettingsInitialized))

        self.assertTrue(events[0].config is conf)
        self.assertTrue(events[1].config is conf)

    def test_settings_initialize_events_exceptions(self):
        self._init_ptah()

        sm = config.registry

        events = []
        err = TypeError()
        def h1(ev):
            raise err

        sm.registerHandler(h1, (config.SettingsInitializing,))
        try:
            config.initialize_settings({}, object())
        except Exception, exc:
            pass

        self.assertIsInstance(exc, config.StopException)
        self.assertIs(exc.exc, err)

    def test_settings_initialize_only_once(self):
        self._init_ptah()
        config.initialize_settings({})

        self.assertRaises(
            RuntimeError,
            config.initialize_settings, {})

    def test_settings_initialize_load_default(self):
        node1 = config.SchemaNode(
                colander.Str(),
                name = 'node1',
                default = 'default1')

        node2 = config.SchemaNode(
                colander.Int(),
                name = 'node2',
                default = 10)

        group = config.register_settings('group', node1, node2)
        self._init_ptah()

        config.initialize_settings({'group.node1': 'setting from ini'})

        self.assertEqual(group['node1'], 'setting from ini')
        self.assertEqual(group['node2'], 10)

    def test_settings_initialize_load_settings_include(self):
        path = os.path.join(self.dir, 'settings.cfg')
        f = open(path, 'wb')
        f.write('[DEFAULT]\ngroup.node1 = value\n\n')
        f.close()

        node1 = config.SchemaNode(
                colander.Str(),
                name = 'node1',
                default = 'default1')

        node2 = config.SchemaNode(
                colander.Int(),
                name = 'node2',
                default = 10)

        group = config.register_settings('group', node1, node2)
        self._init_ptah()

        config.initialize_settings({'include': path})

        self.assertEqual(group['node1'], 'value')
        self.assertEqual(group['node2'], 10)
