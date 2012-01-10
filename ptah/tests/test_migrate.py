import os
import ptah
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
