import sys
import ptah
from ptah.scripts import manage
from pyramid.compat import NativeIO


class TestManageCommand(ptah.PtahTestCase):

    _init_ptah = False

    def test_manage_no_params(self):
        self.init_ptah()

        sys.argv[:] = ['ptah-manage', 'ptah.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        manage.main(False)
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn(
            '[-h] [--list-modules] [--list-models] config', val)

    def test_list_modules(self):

        @ptah.manage.module('custom')
        class CustomModule(ptah.manage.PtahModule):
            """ Custom module description """

            title = 'Custom Module'

        self.init_ptah()

        sys.argv[1:] = ['--list-modules', 'ptah.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        manage.main(False)
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('* custom: Custom Module (disabled: False)', val)
        self.assertIn('Custom module description', val)

        # disable
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH)
        cfg['disable_modules'] = ('custom',)

        out = NativeIO()
        sys.stdout = out

        manage.main(False)
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('* custom: Custom Module (disabled: True)', val)

    def test_list_models(self):
        global CustomModel

        class CustomModel(ptah.cms.Content):
            """ Custom module description """

            title = 'Custom Module'

            __type__ = ptah.cms.Type(
                'custom', title='Custom model',
                description = 'Custom model description')

        self.init_ptah()

        sys.argv[1:] = ['--list-models', 'ptah.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        manage.main(False)
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('* cms-type:custom: Custom model (disabled: False)', val)
        self.assertIn('Custom model description', val)
        self.assertIn('class: CustomModel', val)
        self.assertIn('module: ptah.scripts.tests.test_manage', val)

        # disable
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH)
        cfg['disable_models'] = ('cms-type:custom',)

        out = NativeIO()
        sys.stdout = out

        manage.main(False)
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('* cms-type:custom: Custom model (disabled: True)', val)
