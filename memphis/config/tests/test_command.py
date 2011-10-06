import sys
import unittest, colander
from StringIO import StringIO
from memphis import config
from memphis.config import commands


class BaseTesting(unittest.TestCase):

    def _init_memphis(self, settings={}, *args, **kw):
        config.initialize(('memphis.config', self.__class__.__module__))

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)


class TestCommand(BaseTesting):

    def test_settings_command(self):
        node = config.SchemaNode(
                colander.Str(),
                name = 'node',
                default = 'test')

        group = config.registerSettings(
            'group1', node,
            title = 'Section1',
            description = 'Description1',
            )

        group = config.registerSettings(
            'group2', node,
            title = 'Section2',
            description = 'Description2',
            )

        self._init_memphis()

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
        self.assertEqual(
            val, '[DEFAULT]\ngroup1.node = test\ngroup2.node = test')
