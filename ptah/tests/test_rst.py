from ptah import rst
from ptah.testing import TestCase


class TestRST(TestCase):

    def tearDown(self):
        rst.local_data.sphinx = None

    def test_rst_py_domain(self):
        text = """ Test text :py:class:`ptah.cms.Node` """

        self.assertIn('<span class="pre">ptah.cms.Node</span>',
                      rst.rst_to_html(text))

    def test_rst_error(self):
        text = """ Test text `ptah.cms.Node` """

        self.assertEqual(
            '<pre> Test text `ptah.cms.Node` </pre>', rst.rst_to_html(text))
