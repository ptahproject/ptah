import sys
import ptah
from ptah.scripts import settings
from ptah.testing import PtahTestCase
from pyramid.compat import NativeIO


class TestCommand(PtahTestCase):

    _init_ptah = False

    def test_settings_command(self):
        field = ptah.form.TextField(
            'node',
            default = 'test')

        ptah.register_settings(
            'group1', field,
            title = 'Section1',
            description = 'Description1',
            )

        ptah.register_settings(
            'group2', field,
            title = 'Section2',
            description = 'Description2',
            )

        self.init_ptah()

        group1 = ptah.get_settings('group1', self.registry)
        group2 = ptah.get_settings('group2', self.registry)

        # all
        sys.argv[1:] = ['-a', 'ptah.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        settings.main(False)
        sys.stdout = stdout

        val = out.getvalue()
        self.assertIn('Section1', val)
        self.assertIn('Section2', val)
        self.assertIn('group1.node', val)
        self.assertIn('group2.node', val)

        # section
        sys.argv[1:] = ['-l', 'group1', 'ptah.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        settings.main(False)
        sys.stdout = stdout

        val = out.getvalue()
        self.assertIn('Section1', val)
        self.assertNotIn('Section2', val)
        self.assertIn('group1.node', val)
        self.assertNotIn('group2.node', val)

        # print
        sys.argv[1:] = ['-p', 'ptah.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        settings.main(False)
        sys.stdout = stdout

        val = out.getvalue().strip()
        self.assertIn('group1.node = "test"', val)
        self.assertIn('group2.node = "test"', val)
