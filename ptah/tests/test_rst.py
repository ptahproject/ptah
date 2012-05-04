from ptah import rst
from ptah.testing import TestCase


class TestRST(TestCase):

    def tearDown(self):
        rst.local_data.sphinx = None

    def test_rst_py_domain(self):
        text = """ Test text :py:class:`ptahcms.Node` """

        self.assertIn('span class="pre">ptahcms.Node</span>',
                      rst.rst_to_html(text))

    def test_rst_error(self):
        text = """ Test text `ptahcms.Node` """

        self.assertEqual(
            '<pre> Test text `ptahcms.Node` </pre>', rst.rst_to_html(text))
