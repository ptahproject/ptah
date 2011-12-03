import os
import shutil
import tempfile
import unittest

from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import IObjectEvent

import ptah
from ptah.config.api import objectEventNotify
from ptah.settings import SETTINGS_OB_ID
from ptah.testing import PtahTestCase


def get_settings_ob():
    return ptah.config.get_cfg_storage(SETTINGS_OB_ID)


class BaseTesting(PtahTestCase):

    _init_ptah = False

    def init_ptah(self, *args, **kw):
        ptah.config.initialize(
            self.config, ('ptah', self.__class__.__module__),
            initsettings=False)


class TestSettings(BaseTesting):

    def test_settings_no_default(self):
        field = ptah.form.TextField('node')

        self.assertRaises(
            ptah.config.StopException,
            ptah.register_settings,
            'group1', field,
            title = 'Section title',
            description = 'Section description',
            )

    def test_settings_group_basics(self):
        node = ptah.form.TextField(
            'node',
            default = 'test')

        ptah.register_settings(
            'group1', node,
            title = 'Section title',
            description = 'Section description',
            )
        self.init_ptah()

        group = ptah.get_settings('group1', self.registry)
        self.assertEqual(group.keys(), ['node'])
        self.assertEqual(group.items(), [('node', 'test')])

        group.update({'node': '12345'})
        self.assertEqual(group.get('node'), '12345')

    def test_settings_group_uninitialized(self):
        node = ptah.form.TextField(
            'node',
            default = 'test')

        ptah.register_settings(
            'group1', node,
            title = 'Section title',
            description = 'Section description',
            )
        self.init_ptah()

        group = ptah.get_settings('group1', self.registry)
        self.assertEqual(group.get('node'), 'test')

    def test_settings_get_settings_pyramid(self):
        node = ptah.form.TextField(
            'node',
            default = 'test')

        ptah.register_settings(
            'group1', node,
            title = 'Section title',
            description = 'Section description',
            )

        self.init_ptah()

        grp = self.config.ptah_get_settings('group1')
        self.assertIsNotNone(grp)
        self.assertEqual(grp.__name__, 'group1')
        self.assertIn(node, grp.__fields__.values())

    def test_settings_register_simple(self):
        node = ptah.form.TextField(
            'node',
            default = 'test')

        ptah.register_settings(
            'group1', node,
            title = 'Section title',
            description = 'Section description',
            )

        self.init_ptah()

        group = ptah.get_settings('group1', self.registry)

        self.assertEqual(len(group.__fields__), 1)
        self.assertIn(node, group.__fields__.values())
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
            raise ptah.form.Invalid(node['node'], 'Error')

        node = ptah.form.TextField(
            'node',
            default = 'test')

        group = ptah.register_settings(
            'group2', node, validator=validator)

        self.init_ptah()

        data, err = group.extract({'group2.node': 'value'})

        self.assertEqual(err.msg, {'group2': ['Error']})

    def test_settings_group_multiple_validation(self):
        def validator1(fs, appstruct):
            raise ptah.form.Invalid(fs['node1'], 'Error1')

        def validator2(fs, appstruct):
            raise ptah.form.Invalid(fs['node2'], 'Error2')

        node1 = ptah.form.TextField(
            'node1',
            default = 'test')

        node2 = ptah.form.TextField(
            'node2',
            default = 'test')

        ptah.register_settings(
            'group3', node1, node2, validator=(validator1, validator2))

        self.init_ptah()

        group = ptah.get_settings('group3', self.registry)
        data, err = group.extract({
            'group3.node1': 'value',
            'group3.node2': 'value'})

        self.assertEqual(err.msg, {'group3': ['Error1', 'Error2']})

    def test_settings_export(self):
        field1 = ptah.form.TextField(
            'node1',
            default = 'test')

        field2 = ptah.form.TextField(
            'node2',
            default = 'test1')

        ptah.register_settings('group4', field1, field2)
        self.init_ptah()

        settings = get_settings_ob()

        # changed settings
        self.assertEqual(settings.export(), {})

        # default settings
        data = settings.export(default=True)
        self.assertIn('group4.node1', data)
        self.assertIn('group4.node2', data)
        self.assertEqual(data['group4.node1'], '"test"')
        self.assertEqual(data['group4.node2'], '"test1"')

        # changed settings
        group = ptah.get_settings('group4', self.registry)

        group['node2'] = 'changed'
        data = dict(settings.export())
        self.assertEqual(data['group4.node2'], '"changed"')

    def _create_default_group(self):
        node1 = ptah.form.TextField(
            'node1',
            default = 'default1')

        node2 = ptah.form.IntegerField(
            'node2',
            default = 10)

        ptah.register_settings('group', node1, node2)
        self.init_ptah()

        return ptah.get_settings('group', self.registry)

    def test_settings_load_rawdata(self):
        group = self._create_default_group()

        get_settings_ob().init(self.config, {'group.node1': 'val1'})

        # new value
        self.assertEqual(group['node1'], 'val1')

        # default value
        self.assertEqual(group['node2'], 10)

    def test_settings_load_rawdata_and_change_defaults(self):
        group = self._create_default_group()

        # change defaults
        get_settings_ob().init(self.config, {'group.node2': '30'})

        # new values
        self.assertEqual(group['node1'], 'default1')
        self.assertEqual(group['node2'], 30)

        self.assertEqual(group.__fields__['node1'].default, 'default1')
        self.assertEqual(group.__fields__['node2'].default, 30)

    def test_settings_load_rawdata_with_errors_in_rawdata(self):
        group = self._create_default_group()

        self.assertRaises(
            ptah.config.StopException,
            get_settings_ob().init,
            self.config, {10: 'value'})

    def test_settings_load_defaults_rawdata_with_errors_in_values(self):
        node = ptah.form.LinesField(
            'node1',
            default = ())

        ptah.register_settings('group', node)
        self.init_ptah()

        self.assertRaises(
            ptah.config.StopException,
            get_settings_ob().init,
            self.config,
            {'group.node1': '1,l'})

    def test_settings_init_with_no_loader_with_defaults(self):
        group = self._create_default_group()

        get_settings_ob().init(self.config,
                               {'group.node1': 'new-default',
                                'group.node2': '50'})

        self.assertEqual(group['node1'], 'new-default')
        self.assertEqual(group['node2'], 50)

        self.assertEqual(group.__fields__['node1'].default, 'new-default')
        self.assertEqual(group.__fields__['node2'].default, 50)


class TestSettingsInitialization(BaseTesting):

    def setUp(self):
        ptah.config.cleanup_system()
        BaseTesting.setUp(self)
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        BaseTesting.tearDown(self)
        shutil.rmtree(self.dir)

    def test_settings_initialize_events(self):
        self.init_ptah()

        sm = self.config.registry

        events = []

        def h1(ev):
            events.append(ev)

        def h2(ev):
            events.append(ev)

        sm.registerHandler(h1, (ptah.SettingsInitializing,))
        sm.registerHandler(h2, (ptah.SettingsInitialized,))

        settings = get_settings_ob()

        ptah.initialize_settings(self.config, {})

        self.assertTrue(isinstance(events[0], ptah.SettingsInitializing))
        self.assertTrue(isinstance(events[1], ptah.SettingsInitialized))

        self.assertTrue(events[0].config is self.config)
        self.assertTrue(events[1].config is self.config)

    def test_settings_initialize_events_exceptions(self):
        self.init_ptah()

        sm = self.config.registry

        events = []
        err = TypeError()

        def h1(ev):
            raise err

        sm.registerHandler(h1, (ptah.SettingsInitializing,))
        try:
            ptah.initialize_settings(self.config, {})
        except Exception as exc:
            pass

        self.assertIsInstance(exc, ptah.config.StopException)
        self.assertIs(exc.exc, err)

    def test_settings_initialize_only_once(self):
        self.init_ptah()
        ptah.initialize_settings(self.config, {})

        self.assertRaises(
            RuntimeError,
            ptah.initialize_settings, self.config, {})

    def test_settings_initialize_load_defaults(self):
        node1 = ptah.form.TextField(
            'node1',
            default = 'default1')

        node2 = ptah.form.TextField(
            'node2',
            default = 10)

        ptah.register_settings('group', node1, node2)
        self.init_ptah()

        ptah.initialize_settings(self.config, None)

        group = ptah.get_settings('group', self.request.registry)
        self.assertEqual(group['node1'], 'default1')
        self.assertEqual(group['node2'], 10)

    def test_settings_initialize_load_preparer(self):
        node1 = ptah.form.TextField(
            'node',
            default = 'default1',
            preparer = lambda s: s.lower())

        ptah.register_settings('group', node1)
        self.init_ptah()

        ptah.initialize_settings(self.config, {'group.node': 'Test'})

        group = ptah.get_settings('group', self.request.registry)
        self.assertEqual(group['node'], 'test')

    def test_settings_initialize_load_partly_defaults(self):
        node1 = ptah.form.TextField(
            'node1',
            default = 'default1')

        node2 = ptah.form.TextField(
            'node2',
            default = 10)

        ptah.register_settings('group', node1, node2)
        self.init_ptah()

        ptah.initialize_settings(
            self.config, {'group.node1': 'setting from ini'})

        group = ptah.get_settings('group', self.request.registry)
        self.assertEqual(group['node1'], 'setting from ini')
        self.assertEqual(group['node2'], 10)

    def test_settings_initialize_load_settings_include(self):
        path = os.path.join(self.dir, 'settings.cfg')
        f = open(path, 'wb')
        f.write('[DEFAULT]\ngroup.node1 = value\n\n')
        f.close()

        node1 = ptah.form.TextField(
            'node1',
            default = 'default1')

        node2 = ptah.form.IntegerField(
            'node2',
            default = 10)

        group = ptah.register_settings('group', node1, node2)
        self.init_ptah()

        ptah.initialize_settings(self.config, {'include': path})

        self.assertEqual(group['node1'], 'value')
        self.assertEqual(group['node2'], 10)
