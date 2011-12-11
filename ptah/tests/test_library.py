import ptah
from ptah.testing import PtahTestCase


class TestLibraryManagement(PtahTestCase):

    _init_ptah = False

    def test_library_register_fail(self):
        # path resuired
        self.assertRaises(ValueError, ptah.library, 'test')

        # resource should be registered
        self.assertRaises(ValueError, ptah.library, 'test', path='/test.js')

        # type should be 'js' or 'css'
        self.assertRaises(ValueError, ptah.library,
                          'test', path='/test.js', type='unknown')

    def test_library_simple_css(self):
        self.config.add_static_view('tests30', 'ptah.tests:static/dir1')
        ptah.library('test-lib30',path='style.css',type='css')
        self.init_ptah()

        from ptah.library import LIBRARY_ID
        lib = ptah.get_cfg_storage(LIBRARY_ID)['test-lib30']

        self.assertEqual(lib.name, 'test-lib30')
        self.assertEqual(len(lib.entries), 1)
        self.assertEqual(len(lib.entries), 1)
        self.assertTrue('style.css' in lib.entries[0].paths)

        self.assertEqual(
            repr(lib), '<ptah.Library "test-lib30">')

    def test_library_simple_js(self):
        ptah.library(
            'test-lib', path='http://ptah.org/test.js', type='js')
        self.init_ptah()
        from ptah.library import LIBRARY_ID
        lib = ptah.get_cfg_storage(LIBRARY_ID)['test-lib']

        self.assertEqual(
            lib.render(self.request),
            '<script src="http://ptah.org/test.js"> </script>')

    def test_library_render_absurls(self):
        ptah.library('test-lib', path='http://ptah.org/style.css', type='css')
        self.init_ptah()
        from ptah.library import LIBRARY_ID
        lib = ptah.get_cfg_storage(LIBRARY_ID)['test-lib']

        self.assertEqual(
            lib.render(self.request),
            '<link type="text/css" rel="stylesheet" href="http://ptah.org/style.css" />')

    def test_library_render_with_prefix_postfix(self):
        ptah.library(
            'test-lib', path='http://ptah.org/style.css', type='css',
            prefix='<!--[if lt IE 7 ]>', postfix='<![endif]-->')
        self.init_ptah()
        from ptah.library import LIBRARY_ID
        lib = ptah.get_cfg_storage(LIBRARY_ID)['test-lib']

        self.assertEqual(
            lib.render(self.request),
            '<!--[if lt IE 7 ]><link type="text/css" rel="stylesheet" href="http://ptah.org/style.css" /><![endif]-->')

    def test_library_render_with_extra(self):
        ptah.library(
            'test-lib', path='http://ptah.org/test.js', type='js',
            extra={'test': "extra"})
        self.init_ptah()
        from ptah.library import LIBRARY_ID
        lib = ptah.get_cfg_storage(LIBRARY_ID)['test-lib']

        self.assertEqual(
            lib.render(self.request),
            '<script test="extra" src="http://ptah.org/test.js"> </script>')

    def test_library_include(self):
        ptah.library(
            'test-lib2', path='http://ptah.org/style.css', type='css')
        self.init_ptah()

        ptah.include(self.request, 'test-lib2')
        self.assertEqual(
            ptah.render_includes(self.request),
            '<link type="text/css" rel="stylesheet" href="http://ptah.org/style.css" />')

    def test_library_include_errors(self):
        # render not included
        self.assertEqual(ptah.render_includes(self.request), '')

        # include unknown
        ptah.include(self.request, 'test-lib-test')
        self.assertEqual(ptah.render_includes(self.request), '')

    def test_library_include_recursive(self):
        ptah.library(
            'test-lib1-r', path='http://ptah.org/style1.css', type='css')

        ptah.library(
            'test-lib2-r', path='http://ptah.org/style2.css', type='css',
            require='test-lib1-r')

        ptah.library(
            'test-lib3-r', path='http://ptah.org/style3.css', type='css',
            require=('test-lib1-r', 'test-lib2-r'))

        ptah.library(
            'test-lib4-r', path='http://ptah.org/style4.css', type='css',
            require=('test-lib1-r', 'test-lib2-r'))
        self.init_ptah()

        ptah.include(self.request, 'test-lib3-r')
        ptah.include(self.request, 'test-lib4-r')

        self.assertEqual(
            ptah.render_includes(self.request),
"""<link type="text/css" rel="stylesheet" href="http://ptah.org/style1.css" />
<link type="text/css" rel="stylesheet" href="http://ptah.org/style2.css" />
<link type="text/css" rel="stylesheet" href="http://ptah.org/style3.css" />
<link type="text/css" rel="stylesheet" href="http://ptah.org/style4.css" />""")

    def test_library_include_resource(self):
        self.config.add_static_view('tests30', 'ptah.tests:static/dir1')
        ptah.library(
            'test-lib-30',
            path='ptah.tests:static/dir1/style.css',
            type='css')
        self.init_ptah()

        ptah.include(self.request, 'test-lib-30')

        self.assertEqual(
            ptah.render_includes(self.request),
            '<link type="text/css" rel="stylesheet" href="http://example.com/tests30/style.css" />')

    def test_library_View_include(self):
        ptah.library('test-lib', path='http://ptah.org/test.js', type='js')
        self.init_ptah()

        base = ptah.View(None, self.request)
        base.include('test-lib')

        self.assertEqual(
            base.render_includes(),
            '<script src="http://ptah.org/test.js"> </script>')
