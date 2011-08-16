""" tmpl  """
import unittest
from memphis import view, config


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

    def test_tmpl_multiple_decl(self):
        tmpl = view.template('memphis.view.tests:templates/test.pt')

        self.assertRaises(
            ValueError,
            view.template, 'memphis.view.tests:templates/test.pt')
