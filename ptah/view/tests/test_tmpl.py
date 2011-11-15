""" tmpl  """
import unittest
from ptah import view, config
from ptah.view import tmpl as tapi


class TestTmplCommand(unittest.TestCase):

    def tearDown(self):
        config.cleanup_system()

    def test_tmpl_err1(self):
        self.assertRaises(
            ValueError,
            view.template, 'unkown.pt')

    def test_tmpl_relative(self):
        path, pkg = tapi.path('templates/msg-error.pt')
        self.assertEqual(path, None)
        self.assertEqual(pkg, 'ptah.view.tests')

    def test_tmpl(self):
        tmpl = view.template('ptah.view.tests:templates/test.pt')
        self.assertTrue('PageTemplateFile' in repr(tmpl))

        tmpl = view.template('ptah.view.tests:templates/test.txt')
        self.assertTrue('PageTextTemplateFile' in repr(tmpl))

        self.assertEqual(tapi.registry['ptah.view.tests'].keys(),
                         ['test.pt', 'test.txt'])

    def test_tmpl_multiple_decl(self):
        tmpl = view.template('ptah.view.tests:templates/test.pt')

        tmpl1 = view.template('ptah.view.tests:templates/test.pt')

        self.assertIs(tmpl, tmpl1)

    def test_tmpl_multiple_disable_packages(self):
        view.template('ptah.view.tests:templates/test.pt', nolayer = True)
        view.template('ptah.view.tests:templates/test.pt', nolayer = True)
        self.assertEqual(
            tapi.registry.keys(), [])

    def test_tmpl_multiple_layer_name(self):
        view.template('ptah.view.tests:templates/test.pt', layer = 'test')
        view.template('ptah.view.tests:templates/test.pt')

        self.assertEqual(tapi.registry.keys(), ['test', 'ptah.view.tests'])

    def test_tmpl_multiple_extra_params(self):
        view.template('ptah.view.tests:templates/test.pt',
                      title = 'Test template',
                      description = 'Test template description')

        self.assertEqual(tapi.registry['ptah.view.tests']['test.pt'][1:3],
                         ['Test template', 'Test template description'])
