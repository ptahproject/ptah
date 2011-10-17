import sys
import unittest, colander
from StringIO import StringIO
from ptah import config
from ptah.config import commands


class BaseTesting(unittest.TestCase):

    def _init_ptah(self, settings={}, *args, **kw):
        config.initialize(('ptah.config', self.__class__.__module__))

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)


class TestCommand(BaseTesting):

    def test_settings_command(self):
        node = config.SchemaNode(
                colander.Str(),
                name = 'node',
                default = 'test')

        group = config.register_settings(
            'group1', node,
            title = 'Section1',
            description = 'Description1',
            )

        group = config.register_settings(
            'group2', node,
            title = 'Section2',
            description = 'Description2',
            )

        self._init_ptah()

        # all
        sys.argv[1:] = ['-a']

        stdout = sys.stdout
        out = StringIO()
        sys.stdout = out

        commands.settingsCommand()
        sys.stdout = stdout

        val = out.getvalue()
        self.assertIn('Section1', val)
        self.assertIn('Section2', val)
        self.assertIn('group1.node', val)
        self.assertIn('group2.node', val)

        # section
        sys.argv[1:] = ['-l', 'group1']

        stdout = sys.stdout
        out = StringIO()
        sys.stdout = out

        commands.settingsCommand()
        sys.stdout = stdout

        val = out.getvalue()
        self.assertIn('Section1', val)
        self.assertNotIn('Section2', val)
        self.assertIn('group1.node', val)
        self.assertNotIn('group2.node', val)

        # print
        sys.argv[1:] = ['-p']

        stdout = sys.stdout
        out = StringIO()
        sys.stdout = out

        commands.settingsCommand()
        sys.stdout = stdout

        val = out.getvalue().strip()
        self.assertIn('group1.node = test', val)
        self.assertIn('group2.node = test', val)
