import os
import sys
import shutil
import tempfile
import ptah
from ptah.scripts import migrate
from pyramid.compat import NativeIO


class TestMigrateCommand(ptah.PtahTestCase):

    _init_ptah = False

    def setUp(self):
        super(TestMigrateCommand, self).setUp()

        # fix stdout
        self.orig_stdout = sys.stdout
        self.out = out = NativeIO()
        sys.stdout = out

        # fix bootstrap
        import ptah.scripts
        self.original_bootstrap = ptah.scripts.bootstrap

        def bootstrap(*args, **kw):
            return {'registry': self.registry, 'request': self.request,
                    'app': object()}

        ptah.scripts.bootstrap = bootstrap

        # fix ScriptDirectory
        from ptah import migrate

        self.dirs = dirs = {}

        class ScriptDirectory(migrate.ScriptDirectory):

            def __init__(self, pkg):
                if pkg in dirs:
                    dir = dirs[pkg]
                else:
                    dir = tempfile.mkdtemp()
                    dirs[pkg] = dir

                self.dir = os.path.join(
                    os.path.dirname(ptah.__file__), 'scripts')
                self.versions = dir

        self.orig_ScriptDirectory = migrate.ScriptDirectory
        migrate.ScriptDirectory = ScriptDirectory

    def tearDown(self):
        # reset bootstrap
        import ptah.scripts
        ptah.scripts.bootstrap = self.original_bootstrap

        # reset stdout
        sys.stdout = self.orig_stdout

        # reset ScriptDirectory
        for dir in self.dirs.values():
            shutil.rmtree(dir)

        from ptah import migrate
        migrate.ScriptDirectory = self.orig_ScriptDirectory

        super(TestMigrateCommand, self).tearDown()

    def _reset_stdout(self):
        sys.stdout = self.orig_stdout

    def test_script_help(self):
        self.init_ptah()

        sys.argv[:] = ['ptah-migrate', '-h', 'ptah.ini']

        try:
            migrate.main()
        except:
            pass

        self._reset_stdout()
        self.assertIn('usage: ptah-migrate [-h] config', self.out.getvalue())

    def test_list_migrations(self):
        ptah.register_migration('test', 'test:path', 'Test migration')

        self.init_ptah()

        sys.argv[:] = ['ptah-migrate', 'ptah.ini', 'list']

        migrate.main()

        self._reset_stdout()
        self.assertIn('* test: Test migration', self.out.getvalue())

    def test_upgrade_one(self):
        from ptah.migrate import revision, Version

        ptah.register_migration('test1', 'test1:path', 'Test migration',True)
        ptah.register_migration('test2', 'test2:path', 'Test migration',True)

        self.init_ptah()

        rev1 = revision('test1')
        rev2 = revision('test2')

        sys.argv[:] = ['ptah-migrate', 'ptah.ini', 'upgrade', 'test1']

        migrate.main()

        self._reset_stdout()

        versions = dict((v.package, v.version_num)
                        for v in ptah.get_session().query(Version).all())

        self.assertIn('test1', versions)
        self.assertEqual(versions['test1'], rev1)
        self.assertNotIn('test2', versions)

    def test_upgrade_several(self):
        from ptah.migrate import revision, Version

        ptah.register_migration('test1', 'test1:path', 'Test migration')
        ptah.register_migration('test2', 'test2:path', 'Test migration')

        self.init_ptah()

        versions = dict((v.package, v.version_num)
                        for v in ptah.get_session().query(Version).all())

        rev1 = revision('test1')
        rev2 = revision('test2')

        sys.argv[:] = ['ptah-migrate', 'ptah.ini', 'upgrade', 'test1', 'test2']

        migrate.main()

        self._reset_stdout()

        versions = dict((v.package, v.version_num)
                        for v in ptah.get_session().query(Version).all())

        self.assertIn('test1', versions)
        self.assertIn('test2', versions)
        self.assertEqual(versions['test1'], rev1)
        self.assertEqual(versions['test2'], rev2)

    def test_revision(self):
        from ptah.migrate import revision, Version

        ptah.register_migration('test', 'test:path', 'Test migration')
        self.init_ptah()

        sys.argv[:] = ['ptah-migrate', 'ptah.ini',
                       'revision', 'test', '-r', '001', '-m', 'Test message']
        migrate.main()

        path = self.dirs['test']
        self.assertIn('001.py', os.listdir(path))

    def test_revision_error(self):
        from ptah.migrate import revision, Version

        ptah.register_migration('test', 'test:path', 'Test migration')
        self.init_ptah()

        sys.argv[:] = ['ptah-migrate', 'ptah.ini',
                       'revision', 'test', '-r', '0.0;1', '-m', 'Test message']
        migrate.main()
        self._reset_stdout()

        self.assertIn('Revision id contains forbidden characters',
                      self.out.getvalue())

    def test_history(self):
        from ptah.migrate import revision, upgrade, Version

        ptah.register_migration('test1', 'test1:path', 'Test migration')
        ptah.register_migration('test2', 'test2:path', 'Test migration')

        self.init_ptah()

        rev1 = revision('test1', message='test1 step')
        rev2 = revision('test2', message='test2 step')

        upgrade('test1')
        upgrade('test2')

        sys.argv[:] = ['ptah-migrate', 'ptah.ini', 'history', 'test1']

        migrate.main()

        self.assertIn('test1 step', self.out.getvalue())

        sys.argv[:] = ['ptah-migrate', 'ptah.ini', 'history']
        migrate.main()

        self.assertIn('test1 step', self.out.getvalue())
        self.assertIn('test2 step', self.out.getvalue())

    def test_current_one(self):
        from ptah.migrate import revision, upgrade, Version

        ptah.register_migration('test1', 'test1:path', 'Test migration')
        ptah.register_migration('test2', 'test2:path', 'Test migration')

        self.init_ptah()

        rev1 = revision('test1', message='test1 step')
        rev2 = revision('test2', message='test2 step')
        upgrade('test1')

        sys.argv[:] = ['ptah-migrate', 'ptah.ini', 'current', 'test1']

        migrate.main()

        self.assertIn("Package 'test1' rev: %s(head) test1 step"%rev1,
                      self.out.getvalue())

    def test_current_all(self):
        from ptah.migrate import revision, upgrade, Version

        ptah.register_migration('test1', 'test1:path', 'Test migration')
        ptah.register_migration('test2', 'test2:path', 'Test migration')

        self.init_ptah()

        rev1 = revision('test1', message='test1 step')
        rev2 = revision('test2', message='test2 step')
        upgrade('test1')

        sys.argv[:] = ['ptah-migrate', 'ptah.ini', 'current']

        migrate.main()

        self.assertIn("Package 'test1' rev: %s(head) test1 step"%rev1,
                      self.out.getvalue())
        self.assertIn("Package 'test2' rev: None", self.out.getvalue())
