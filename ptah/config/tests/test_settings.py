import sys, os, time
import unittest, shutil, tempfile, colander
from zope.interface.registry import Components
from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import IObjectEvent

from ptah import config
from ptah.config.api import objectEventNotify
from ptah.config.settings import \
    FileStorage, iNotifyWatcher, shutdown_handler, get_settings


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

        self.assertEqual(get_settings()._changed, None)

        group.node = 'test2'
        self.assertFalse(group.node == group['node'])

        group['node'] =  'test2'
        self.assertTrue('group1' in get_settings()._changed)
        self.assertTrue('node' in get_settings()._changed['group1'])

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

    def test_settings_load_rawdata_and_send_modified_event(self):
        group = self._create_default_group()

        sm = config.registry

        events = []
        def h(grp, ev):
            events.append((grp is group, ev))

        sm.registerHandler(h, (group.category, config.SettingsGroupModified))

        get_settings()._load({'group.node1': 'value'}, suppressevents=False)

        self.assertTrue(events[0][0])
        self.assertTrue(isinstance(events[0][1], config.SettingsGroupModified))
        self.assertTrue(events[0][1].object is group)

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

    def test_settings_init_with_no_loader(self):
        group = self._create_default_group()

        get_settings().init(None)

        # initialized with defaults
        self.assertEqual(dict(group), {'node1': 'default1', 'node2': 10})

    def test_settings_init_with_no_loader_with_defaults(self):
        group = self._create_default_group()

        get_settings().init(None,
                            {'group.node1': 'new-default',
                             'group.node2': 50})

        self.assertEqual(group['node1'], 'new-default')
        self.assertEqual(group['node2'], 50)

        self.assertEqual(group.schema['node1'].default, 'new-default')
        self.assertEqual(group.schema['node2'].default, 50)

    def test_settings_init_with_loader_values(self):
        class Loader(object):
            def load(self):
                return {
                    'group.node1': 'new-value',
                    'group.node2': 60}

        group = self._create_default_group()
        get_settings().init(Loader())

        self.assertEqual(group['node1'], 'new-value')
        self.assertEqual(group['node2'], 60)

        self.assertEqual(group.schema['node1'].default, 'default1')
        self.assertEqual(group.schema['node2'].default, 10)

    def test_settings_reload_from_loader(self):
        class Loader(object):
            def load(self):
                return {'group.node1': 'new-value',
                        'group.node2': 60}

        group = self._create_default_group()
        get_settings().init(Loader())

        group['node1'] = 'val'
        group['node2'] = 90

        self.assertEqual(group['node1'], 'val')
        self.assertEqual(group['node2'], 90)

        get_settings().load()
        self.assertEqual(group['node1'], 'new-value')
        self.assertEqual(group['node2'], 60)

    def test_settings_save(self):
        class Loader(object):
            def load(self):
                return {}
            def save(self, data):
                saved.update(data)

        saved = {}

        group = self._create_default_group()
        get_settings().init(Loader())

        get_settings().save()
        self.assertEqual(saved, {})

        sm = config.registry

        events = []

        def h(grp, ev):
            events.append((grp is group, ev))

        sm.registerHandler(h, (group.category, config.SettingsGroupModified))
        sm.registerHandler(objectEventNotify, (IObjectEvent,))

        group['node1'] = 'val'
        group['node2'] = 90

        get_settings().save()

        self.assertEqual(saved, {'group.node1': 'val', 'group.node2': '90'})
        self.assertTrue(len(events) == 1)


class TestFileStorage(BaseTesting):

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_settings_fs_no_fails(self):
        fs = FileStorage(None, None)

        self.assertEqual(fs.watcher, None)
        self.assertEqual(fs.load(), {})
        self.assertEqual(fs.close(), None)

    def test_settings_fs(self):
        path = os.path.join(self.dir, 'settings.cfg')
        f = open(path, 'wb')
        f.write("""[DEFAULT]\ngroup.node1 = test\ngroup.node2 = 40""")
        f.close()

        fs = FileStorage(None, path)
        self.assertEqual(fs.load(),
                         {'group.node1': 'test',
                          'group.node2': '40', 'here': ''})

    def test_settings_fs_nosettings_file(self):
        path = os.path.join(self.dir, 'settings.cfg')

        fs = FileStorage(None, path)
        self.assertEqual(fs.load(), {'here': ''})
        self.assertTrue(os.path.exists(path))

    def test_settings_fs_save_nosettings_file(self):
        fs = FileStorage(None, None)
        self.assertEqual(fs.save({'group.node1': 'test'}), None)

    def test_settings_fs_save(self):
        path = os.path.join(self.dir, 'settings.cfg')

        fs = FileStorage(None, path)
        self.assertEqual(fs.load(), {'here': ''})

        fs.save({'group.node1': 'value'})
        self.assertEqual(fs.load(), {'group.node1': 'value', 'here': ''})
        self.assertEqual(open(path).read(),
                         '[DEFAULT]\ngroup.node1 = value\n\n')

    def test_settings_fs_save_to_existing(self):
        path = os.path.join(self.dir, 'settings.cfg')
        f = open(path, 'wb')
        f.write('[TEST]\ngroup.node1 = value\n\n')
        f.close()

        fs = FileStorage(None, path)
        self.assertEqual(fs.load(), {'here': ''})

        fs.save({'group.node1': 'value'})
        self.assertEqual(fs.load(), {'group.node1': 'value', 'here': ''})
        self.assertEqual(
            open(path).read(),
            '[DEFAULT]\ngroup.node1 = value\n\n[TEST]\ngroup.node1 = value\n\n')

    def test_settings_fs_save_to_existing_diff_sect(self):
        path = os.path.join(self.dir, 'settings.cfg')
        f = open(path, 'wb')
        f.write('[DEFAULT]\ngroup.node = value\n\n')
        f.close()

        fs = FileStorage(None, path, section='TEST')
        self.assertEqual(fs.load(), {})

        fs.save({'group.node3': 'value'})

        #self.assertEqual(fs.load(), {'group.node3': 'value', 'here': ''})
        self.assertEqual(
            open(path).read(),
            '[DEFAULT]\ngroup.node = value\n\n[TEST]\ngroup.node3 = value\n\n')


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

        self.assertTrue(settings.loader is None)

        conf = object()
        config.initialize_settings({}, conf)

        self.assertTrue(isinstance(events[0], config.SettingsInitializing))
        self.assertTrue(isinstance(events[1], config.SettingsInitialized))

        self.assertTrue(events[0].config is conf)
        self.assertTrue(events[1].config is conf)

        self.assertTrue(isinstance(settings.loader, FileStorage))

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

    def test_settings_initialize_load_settings_from_file(self):
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

        config.initialize_settings({'settings': path})

        self.assertEqual(group['node1'], 'value')
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

    @unittest.skipUnless(sys.platform == 'linux2', 'linux specific')
    def test_settings_fs_watcher(self):
        path = os.path.join(self.dir, 'settings.cfg')
        f = open(path, 'wb')
        f.write('[DEFAULT]\ngroup.node1 = value\n\n')
        f.close()

        node1 = config.SchemaNode(
                colander.Str(),
                name = 'node1',
                default = 'default1')

        group = config.register_settings('group', node1)
        self._init_ptah()

        class Config(object):
            def begin(self): # pragma: no cover
                pass
            def end(self): # pragma: no cover
                pass

        config.initialize_settings({'settings': path}, config=Config())

        settings = get_settings()

        self.assertTrue(
            isinstance(settings.loader.watcher, iNotifyWatcher))
        self.assertEqual(group['node1'], 'value')

        f = open(path, 'wb')
        f.write('[DEFAULT]\ngroup.node1 = new_value\n\n')
        f.close()
        time.sleep(0.2)

        self.assertEqual(group['node1'], 'new_value')
        self.assertTrue(settings.loader.watcher.started)

        shutdown_handler()
        self.assertFalse(settings.loader.watcher.started)
