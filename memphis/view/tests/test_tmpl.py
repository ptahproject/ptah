""" tmpl  """
import unittest
from memphis import view, config
from memphis.view import tmpl as tapi


class TestTmplCommand(unittest.TestCase):

    def tearDown(self):
        config.cleanUp()

    def test_tmpl_err1(self):
        self.assertRaises(
            ValueError,
            view.template, 'unkown.pt')

    def test_tmpl(self):
        tmpl = view.template('memphis.view.tests:templates/test.pt')
        self.assertTrue('PageTemplateFile' in repr(tmpl))

        tmpl = view.template('memphis.view.tests:templates/test.txt')
        self.assertTrue('PageTextTemplateFile' in repr(tmpl))

        self.assertEqual(tapi.registry['memphis.view.tests'].keys(),
                         ['test.pt', 'test.txt'])

    def test_tmpl_multiple_decl(self):
        tmpl = view.template('memphis.view.tests:templates/test.pt')

        self.assertRaises(
            ValueError,
            view.template, 'memphis.view.tests:templates/test.pt')

    def test_tmpl_multiple_disable_packages(self):
        tmpl = view.template('memphis.view.tests:templates/test.pt',
                             nolayer = True)
        tmpl = view.template('memphis.view.tests:templates/test.pt',
                             nolayer = True)
        self.assertEqual(
            tapi.registry.keys(), [])

    def test_tmpl_multiple_layer_name(self):
        tmpl = view.template('memphis.view.tests:templates/test.pt',
                             layer = 'test')
        tmpl = view.template('memphis.view.tests:templates/test.pt')

        self.assertEqual(tapi.registry.keys(), ['test', 'memphis.view.tests'])

    def test_tmpl_multiple_extra_params(self):
        tmpl = view.template('memphis.view.tests:templates/test.pt',
                             title = 'Test template',
                             description = 'Test template description')

        self.assertEqual(tapi.registry['memphis.view.tests']['test.pt'][1:3],
                         ['Test template', 'Test template description'])
