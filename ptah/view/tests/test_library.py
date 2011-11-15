from ptah import config, view

from base import Base


class TestLibraryManagement(Base):

    def _setup_ptah(self):
        pass

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestLibraryManagement, self).tearDown()

    def test_library_register_fail(self):
        # path resuired
        self.assertRaises(ValueError, view.library, 'test')

        # resource should be registered
        self.assertRaises(ValueError, view.library,
                          'test', path='/test.js', resource='unknown')

        # type should be 'js' or 'css'
        self.assertRaises(ValueError, view.library,
                          'test', path='/test.js', type='unknown')

        # if not resource is provided, path has to be absolute url
        self.assertRaises(ValueError, view.library,
                          'test', path='/test.js', type='js')

    def test_library_simple_css(self):
        view.static('tests', 'ptah.view.tests:static/dir1')

        view.library(
            'test-lib', path='style.css', resource='tests', type='css')
        self._init_ptah()

        from ptah.view.library import LIBRARY_ID
        lib = config.get_cfg_storage(LIBRARY_ID)['test-lib']

        self.assertEqual(lib.name, 'test-lib')
        self.assertEqual(len(lib.entries), 1)
        self.assertEqual(len(lib.entries), 1)
        self.assertTrue('style.css' in lib.entries[0].paths)

        self.assertEqual(
            repr(lib), '<ptah.view.library.Library "test-lib">')

    def test_library_simple_js(self):
        view.library(
            'test-lib', path='http://ptah.org/test.js', type='js')
        self._init_ptah()
        from ptah.view.library import LIBRARY_ID
        lib = config.get_cfg_storage(LIBRARY_ID)['test-lib']

        self.assertEqual(
            lib.render(self.request),
            '<script src="http://ptah.org/test.js"> </script>')

    def test_library_render_absurls(self):
        view.library(
            'test-lib', path='http://ptah.org/style.css', type='css')
        self._init_ptah()
        from ptah.view.library import LIBRARY_ID
        lib = config.get_cfg_storage(LIBRARY_ID)['test-lib']

        self.assertEqual(
            lib.render(self.request),
            '<link type="text/css" rel="stylesheet" href="http://ptah.org/style.css" />')

    def test_library_render_with_prefix_postfix(self):
        view.library(
            'test-lib', path='http://ptah.org/style.css', type='css',
            prefix='<!--[if lt IE 7 ]>', postfix='<![endif]-->')
        self._init_ptah()
        from ptah.view.library import LIBRARY_ID
        lib = config.get_cfg_storage(LIBRARY_ID)['test-lib']

        self.assertEqual(
            lib.render(self.request),
            '<!--[if lt IE 7 ]><link type="text/css" rel="stylesheet" href="http://ptah.org/style.css" /><![endif]-->')

    def test_library_render_with_extra(self):
        view.library(
            'test-lib', path='http://ptah.org/test.js', type='js',
            extra={'test': "extra"})
        self._init_ptah()
        from ptah.view.library import LIBRARY_ID
        lib = config.get_cfg_storage(LIBRARY_ID)['test-lib']

        self.assertEqual(
            lib.render(self.request),
            '<script test="extra" src="http://ptah.org/test.js"> </script>')

    def test_library_include(self):
        view.library(
            'test-lib', path='http://ptah.org/style.css', type='css')
        self._init_ptah()

        view.include(self.request, 'test-lib')
        self.assertEqual(
            view.render_includes(self.request),
            '<link type="text/css" rel="stylesheet" href="http://ptah.org/style.css" />')

    def test_library_include_errors(self):
        # render not included
        self.assertEqual(view.render_includes(self.request), '')

        # include unknown
        view.include(self.request, 'test-lib-test')
        self.assertEqual(view.render_includes(self.request), '')

    def test_library_include_recursive(self):
        view.library(
            'test-lib1', path='http://ptah.org/style1.css', type='css')

        view.library(
            'test-lib2', path='http://ptah.org/style2.css', type='css',
            require='test-lib1')

        view.library(
            'test-lib3', path='http://ptah.org/style3.css', type='css',
            require=('test-lib1', 'test-lib2'))

        view.library(
            'test-lib4', path='http://ptah.org/style4.css', type='css',
            require=('test-lib1', 'test-lib2'))
        self._init_ptah()

        view.include(self.request, 'test-lib3')
        view.include(self.request, 'test-lib4')

        self.assertEqual(
            view.render_includes(self.request),
"""<link type="text/css" rel="stylesheet" href="http://ptah.org/style1.css" />
<link type="text/css" rel="stylesheet" href="http://ptah.org/style2.css" />
<link type="text/css" rel="stylesheet" href="http://ptah.org/style3.css" />
<link type="text/css" rel="stylesheet" href="http://ptah.org/style4.css" />""")

    def test_library_include_resource(self):
        view.static('tests2', 'ptah.view.tests:static/dir1')
        view.library(
            'test-lib', path='style.css', resource='tests2', type='css')
        self._init_ptah()

        request = self._makeRequest()

        view.include(request, 'test-lib')

        self.assertEqual(
            view.render_includes(request),
            '<link type="text/css" rel="stylesheet" href="http://localhost:8080/static/tests2/style.css" />')

    def test_library_View_include(self):
        view.library('test-lib', path='http://ptah.org/test.js', type='js')
        self._init_ptah()

        base = view.View(None, self.request)
        base.include('test-lib')

        self.assertEqual(
            base.render_includes(),
            '<script src="http://ptah.org/test.js"> </script>')
