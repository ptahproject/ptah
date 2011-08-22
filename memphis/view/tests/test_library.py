""" """
import unittest
from memphis import config, view

from base import Base

       
class TestLibraryManagement(Base):

    def _setup_memphis(self):
        pass

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
        view.static('tests', 'memphis.view.tests:static/dir1')
        self._init_memphis()

        lib = view.library(
            'test-lib', path='style.css', resource='tests', type='css')
    
        self.assertEqual(lib.name, 'test-lib')
        self.assertEqual(len(lib.entries), 1)
        self.assertEqual(len(lib.entries), 1)
        self.assertTrue('style.css' in lib.entries[0].paths)

        self.assertEqual(
            repr(lib), '<memphis.view.library.Library "test-lib">')

    def test_library_simple_js(self):
        lib = view.library(
            'test-lib', path='http://memphis.org/test.js', type='js')

        self.assertEqual(
            lib.render(self.request),
            '<script src="http://memphis.org/test.js"> </script>')

    def test_library_render_absurls(self):
        lib = view.library(
            'test-lib', path='http://memphis.org/style.css', type='css')
    
        self.assertEqual(
            lib.render(self.request),
            '<link type="text/css" rel="stylesheet" href="http://memphis.org/style.css" />')

    def test_library_render_with_prefix_postfix(self):
        lib = view.library(
            'test-lib', path='http://memphis.org/style.css', type='css',
            prefix='<!--[if lt IE 7 ]>', postfix='<![endif]-->')

        self.assertEqual(
            lib.render(self.request),
            '<!--[if lt IE 7 ]><link type="text/css" rel="stylesheet" href="http://memphis.org/style.css" /><![endif]-->')

    def test_library_render_with_extra(self):
        lib = view.library(
            'test-lib', path='http://memphis.org/test.js', type='js',
            extra={'test': "extra"})

        self.assertEqual(
            lib.render(self.request),
            '<script test="extra" src="http://memphis.org/test.js"> </script>')

    def test_library_include(self):
        lib = view.library(
            'test-lib', path='http://memphis.org/style.css', type='css')

        view.include('test-lib', self.request)
        self.assertEqual(
            view.renderIncludes(self.request),
            '<link type="text/css" rel="stylesheet" href="http://memphis.org/style.css" />')

    def test_library_include_errors(self):
        # render not included
        self.assertEqual(view.renderIncludes(self.request), '')

        # include unknown
        view.include('test-lib', self.request)
        self.assertEqual(view.renderIncludes(self.request), '')       

    def test_library_include_recursive(self):
        lib1 = view.library(
            'test-lib1', path='http://memphis.org/style1.css', type='css')

        lib2 = view.library(
            'test-lib2', path='http://memphis.org/style2.css', type='css',
            require='test-lib1')

        lib3 = view.library(
            'test-lib3', path='http://memphis.org/style3.css', type='css',
            require=('test-lib1', 'test-lib2'))

        lib4 = view.library(
            'test-lib4', path='http://memphis.org/style4.css', type='css',
            require=('test-lib1', 'test-lib2'))

        view.include('test-lib3', self.request)
        view.include('test-lib4', self.request)

        self.assertEqual(
            view.renderIncludes(self.request),
"""<link type="text/css" rel="stylesheet" href="http://memphis.org/style1.css" />
<link type="text/css" rel="stylesheet" href="http://memphis.org/style2.css" />
<link type="text/css" rel="stylesheet" href="http://memphis.org/style3.css" />
<link type="text/css" rel="stylesheet" href="http://memphis.org/style4.css" />""")

    def test_library_include_resource(self):
        view.static('tests2', 'memphis.view.tests:static/dir1')
        self._init_memphis()

        lib = view.library(
            'test-lib', path='style.css', resource='tests2', type='css')

        request = self._makeRequest()

        view.include('test-lib', request)

        self.assertEqual(
            view.renderIncludes(request),
            '<link type="text/css" rel="stylesheet" href="http://localhost:8080/static/tests2/style.css" />')

    def test_library_View_include(self):
        lib = view.library(
            'test-lib', path='http://memphis.org/test.js', type='js')

        base = view.View(None, self.request)
        base.include('test-lib')

        self.assertEqual(
            base.renderIncludes(),
            '<script src="http://memphis.org/test.js"> </script>')
