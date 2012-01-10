import os
import ptah
import shutil
import tempfile
from pyramid.config import ConfigurationConflictError


class TestRegisterMigration(ptah.PtahTestCase):

    _init_ptah = False

    def test_register(self):
        from ptah.migrate import MIGRATION_ID

        ptah.register_migration(
            'test', 'ptah.tests:migrations', 'Ptah database migration')
        self.init_ptah()

        st = ptah.get_cfg_storage(MIGRATION_ID)

        self.assertIn('test', st)
        self.assertEqual(st['test'], 'ptah.tests:migrations')

    def test_register_conflict(self):
        from ptah.migrate import MIGRATION_ID

        ptah.register_migration(
            'test', 'ptah.tests:migrations', 'Ptah database migration')
        ptah.register_migration(
            'test', 'ptah.tests:migrations', 'Ptah database migration')

        self.assertRaises(ConfigurationConflictError, self.init_ptah)


class TestPyramidDirective(ptah.PtahTestCase):

    def setUp(self):
        from ptah import migrate

        self._pkgs = []
        def upgrade(pkg):
            self._pkgs.append(pkg)

        self.orig_upgrade = migrate.upgrade
        migrate.upgrade = upgrade

        super(TestPyramidDirective, self).setUp()

    def tearDown(self):
        super(TestPyramidDirective, self).tearDown()

        from ptah import migrate
        migrate.upgrade = self.orig_upgrade

    def test_pyramid_directive(self):
        from pyramid.config import Configurator

        config = Configurator()
        config.include('ptah')

        self.assertTrue(hasattr(config, 'ptah_migrate'))

    def test_directive_execution(self):
        from pyramid.config import Configurator

        config = Configurator()
        config.include('ptah')
        config.ptah_migrate()
        config.commit()

        self.assertEqual(self._pkgs, ['ptah'])


class TestScriptDirectory(ptah.PtahTestCase):

    _init_ptah = False

    def test_unknown_package(self):
        self.init_ptah()

        from ptah.migrate import ScriptDirectory

        self.assertRaises(ValueError, ScriptDirectory, 'unknown')

    def test_normal(self):
        self.init_ptah()

        from ptah.migrate import ScriptDirectory

        script = ScriptDirectory('ptah')

        self.assertEqual(
            script.dir,
            os.path.join(os.path.dirname(ptah.__file__), 'scripts'))

        self.assertEqual(
            script.versions,
            os.path.join(os.path.dirname(ptah.__file__), 'migrations'))

    def test_doesnt_exist(self):
        from alembic.util import CommandError
        from ptah.migrate import ScriptDirectory

        ptah.register_migration('test', 'ptah:unknown_migrations')
        self.init_ptah()

        self.assertRaises(CommandError, ScriptDirectory, 'test')


class TestRevision(ptah.PtahTestCase):

    def setUp(self):
        from ptah import migrate

        dir = self.dir = tempfile.mkdtemp()

        class ScriptDirectory(migrate.ScriptDirectory):

            def __init__(self, pkg):
                self.dir = os.path.join(
                    os.path.dirname(ptah.__file__), 'scripts')
                self.versions = dir

        self.orig_ScriptDirectory = migrate.ScriptDirectory
        migrate.ScriptDirectory = ScriptDirectory

        super(TestRevision, self).setUp()

    def tearDown(self):
        super(TestRevision, self).tearDown()

        shutil.rmtree(self.dir)

        from ptah import migrate
        migrate.ScriptDirectory = self.orig_ScriptDirectory

    def test_revision_default(self):
        from ptah.migrate import revision

        rev = revision('test', message='Test message')
        self.assertIn('{0}.py'.format(rev), os.listdir(self.dir))

    def test_revision_custom(self):
        from ptah.migrate import revision

        rev = revision('test', rev='001', message='Test message')
        self.assertEqual(rev, '001')
        self.assertIn('001.py', os.listdir(self.dir))

        self.assertRaises(
            KeyError, revision, 'test', rev='001')
