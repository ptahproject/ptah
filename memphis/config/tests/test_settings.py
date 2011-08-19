""" """
import unittest, os, shutil, tempfile, colander
from memphis import config
from memphis.config.settings import FileStorage
from zope.component import getSiteManager
from zope.interface.interface import InterfaceClass


class BaseTesting(unittest.TestCase):

    def _init_memphis(self, settings={}, *args, **kw):
        config.begin()
        config.loadPackage('memphis.config')
        config.addPackage(self.__class__.__module__)
        config.commit()

    def tearDown(self):
        config.cleanUp()


class TestSettings(BaseTesting):

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

    def test_settings_group_validation(self):
        def validator(node, appstruct):
            raise colander.Invalid(node['node'], 'Error')

        node = config.SchemaNode(
                colander.Str(),
                name = 'node',
                default = 'test')

        group = config.registerSettings(
            'group2', node, validator=validator)

        self._init_memphis()

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

        group = config.registerSettings(
            'group3', node1, node2, validator=(validator1, validator2))

        self._init_memphis()

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

        group = config.registerSettings('group4', node1, node2)

        self._init_memphis()

        # changed settings
        self.assertEqual(config.Settings.export(), {})

        # default settings
        self.assertEqual(config.Settings.export(default=True),
                         {'group4.node1': 'test', 'group4.node2': 'test'})

        # changed settings
        group['node2'] = 'changed'
        data = dict(config.Settings.export())
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

        group = config.registerSettings('group', node1, node2)
        self._init_memphis()

        group.clear()

        return group

    def test_settings_load_rawdata(self):
        group = self._create_default_group()

        config.Settings._load({'group.node1': 'val1'})

        # new value
        self.assertEqual(group['node1'], 'val1')

        # default value
        self.assertEqual(group['node2'], 10)

    def test_settings_load_rawdata_and_change_defaults(self):
        group = self._create_default_group()

        # change defaults
        config.Settings._load({'group.node2': 30}, setdefaults=True)

        # new values
        self.assertEqual(group['node1'], 'default1')
        self.assertEqual(group['node2'], 30)

        self.assertEqual(group.schema['node1'].default, 'default1')
        self.assertEqual(group.schema['node2'].default, 30)

    def test_settings_load_rawdata_and_send_modified_event(self):
        group = self._create_default_group()

        sm = getSiteManager()
        
        events = []
        def h(grp, ev):
            events.append((grp is group, ev))

        sm.registerHandler(h, (group.category, config.SettingsGroupModified))

        group.clear()
        config.Settings._load({'group.node1': 'value'}, suppressevents=False)

        self.assertTrue(events[0][0])
        self.assertTrue(isinstance(events[0][1], config.SettingsGroupModified))
        self.assertTrue(events[0][1].object is group)

    def test_settings_load_rawdata_with_errors_in_rawdata(self):
        group = self._create_default_group()

        config.Settings._load({10: 'value'})
        self.assertEqual(group, {})

    def test_settings_load_rawdata_with_errors_in_values(self):
        group = self._create_default_group()

        config.Settings._load({'group.node2': 'vadfw234lue'})
        self.assertEqual(group, {'node1': 'default1', 'node2': 10})

    def test_settings_load_defaults_rawdata_with_errors_in_values(self):
        group = self._create_default_group()

        config.Settings._load({'group.node2': 'vadfw234lue'}, setdefaults=True)
        self.assertEqual(group, {})

    def test_settings_init_with_no_loader(self):
        group = self._create_default_group()
        self.assertEqual(group, {})

        config.Settings.init(None)

        # initialized with defaults
        self.assertEqual(group, {'node1': 'default1', 'node2': 10})

    def test_settings_init_with_no_loader_with_defaults(self):
        group = self._create_default_group()

        config.Settings.init(None,
                             {'group.node1': 'new-default',
                              'group.node2': 50})

        self.assertEqual(group['node1'], 'new-default')
        self.assertEqual(group['node2'], 50)

        self.assertEqual(group.schema['node1'].default, 'new-default')
        self.assertEqual(group.schema['node2'].default, 50)

    def test_settings_init_with_loader_defaults(self):
        class Loader(object):
            def load(self):
                return {}

            def loadDefaults(self):
                return {'group.node1': 'new-default',
                        'group.node2': 50}

            def close(self):
                pass

        group = self._create_default_group()
        config.Settings.init(Loader())
        
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

            def loadDefaults(self):
                return {}

            def close(self):
                pass

        group = self._create_default_group()
        config.Settings.init(Loader())
        
        self.assertEqual(group['node1'], 'new-value')
        self.assertEqual(group['node2'], 60)

        self.assertEqual(group.schema['node1'].default, 'default1')
        self.assertEqual(group.schema['node2'].default, 10)

    def test_settings_init_with_loader_override_defaults_defaults(self):
        class Loader(object):
            def load(self):
                return {}

            def loadDefaults(self):
                return {'group.node1': 'new-value',
                        'group.node2': 60}

            def close(self):
                pass

        group = self._create_default_group()
        config.Settings.init(Loader(),
                             {'group.node1': 'new-default',
                              'group.node2': 50})
        
        self.assertEqual(group['node1'], 'new-value')
        self.assertEqual(group['node2'], 60)

        self.assertEqual(group.schema['node1'].default, 'new-value')
        self.assertEqual(group.schema['node2'].default, 60)

    def test_settings_init_with_loader_override_defaults(self):
        class Loader(object):
            def load(self):
                return {'group.node1': 'new-value',
                        'group.node2': 60}

            def loadDefaults(self):
                return {'group.node1': 'new-default',
                        'group.node2': 50}

            def close(self):
                pass

        group = self._create_default_group()
        config.Settings.init(Loader())
        
        self.assertEqual(group['node1'], 'new-value')
        self.assertEqual(group['node2'], 60)

        self.assertEqual(group.schema['node1'].default, 'new-default')
        self.assertEqual(group.schema['node2'].default, 50)

    def test_settings_reload_from_loader(self):
        class Loader(object):
            def load(self):
                return {'group.node1': 'new-value',
                        'group.node2': 60}

            def loadDefaults(self):
                return {}

            def close(self):
                pass

        group = self._create_default_group()
        config.Settings.init(Loader())
        
        group['node1'] = 'val'
        group['node2'] = 90

        self.assertEqual(group['node1'], 'val')
        self.assertEqual(group['node2'], 90)

        config.Settings.load()
        self.assertEqual(group['node1'], 'new-value')
        self.assertEqual(group['node2'], 60)

    def test_settings_save(self):
        class Loader(object):
            def load(self):
                return {}
            def loadDefaults(self):
                return {}
            def close(self):
                pass
            def save(self, data):
                saved.update(data)

        saved = {}

        group = self._create_default_group()
        config.Settings.init(Loader())
        
        config.Settings.save()
        self.assertEqual(saved, {})

        sm = getSiteManager()
        
        events = []
        def h(grp, ev):
            events.append((grp is group, ev))

        sm.registerHandler(h, (group.category, config.SettingsGroupModified))

        group['node1'] = 'val'
        group['node2'] = 90

        config.Settings.save()
        self.assertEqual(saved, {'group.node1': 'val', 'group.node2': '90'})
        self.assertTrue(len(events) == 1)


class TestFileStorage(BaseTesting):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_settings_fs_no_fails(self):
        fs = FileStorage(None)

        self.assertEqual(fs.watcher, None)
        self.assertEqual(fs.load(), {})
        self.assertEqual(fs.loadDefaults(), {})
        self.assertEqual(fs.close(), None)

    def test_settings_fs_notexisting_defaults(self):
        fs = FileStorage(None, os.path.join(self.dir, 'defaults.cfg'))

        self.assertEqual(fs.loadDefaults(), {})

    def test_settings_fs_defaults(self):
        path = os.path.join(self.dir, 'defaults.cfg')
        f = open(path, 'wb')
        f.write("""[DEFAULT]\ngroup.node1 = test\ngroup.node2 = 40""")
        f.close()

        fs = FileStorage(None, os.path.join(self.dir, 'defaults.cfg'))

        self.assertEqual(fs.loadDefaults(), 
                         {'group.node1': 'test',
                          'group.node2': '40', 'here': ''})

    def test_settings_fs_defaults(self):
        path = os.path.join(self.dir, 'defaults.cfg')
        f = open(path, 'wb')
        f.write("""[DEFAULT]\ngroup.node1 = test\ngroup.node2 = 40""")
        f.close()

        fs = FileStorage(None, path)

        self.assertEqual(fs.loadDefaults(), 
                         {'group.node1': 'test',
                          'group.node2': '40', 'here': ''})

    def test_settings_fs_defaults_include(self):
        path_extra = os.path.join(self.dir, 'defaults-extra.cfg')
        f = open(path_extra, 'wb')
        f.write("""[DEFAULT]\nsection.item = 40""")
        f.close()

        path = os.path.join(self.dir, 'defaults.cfg')
        f = open(path, 'wb')
        f.write("[DEFAULT]\ngroup.node = test\ninclude = %s"%path_extra)
        f.close()

        fs = FileStorage(None, path)
        data = fs.loadDefaults()

        self.assertTrue('group.node' in data)
        self.assertTrue('section.item' in data)
        self.assertEqual([data['group.node'], data['section.item']],
                         ['test', '40'])

    def test_settings_fs(self):
        path = os.path.join(self.dir, 'settings.cfg')
        f = open(path, 'wb')
        f.write("""[DEFAULT]\ngroup.node1 = test\ngroup.node2 = 40""")
        f.close()

        fs = FileStorage(path)
        self.assertEqual(fs.load(), 
                         {'group.node1': 'test',
                          'group.node2': '40', 'here': ''})

    def test_settings_fs_nosettings_file(self):
        path = os.path.join(self.dir, 'settings.cfg')
        
        fs = FileStorage(path)
        self.assertEqual(fs.load(), {'here': ''})
        self.assertTrue(os.path.exists(path))

