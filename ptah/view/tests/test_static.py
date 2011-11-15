""" test for static assets api """
import os.path
from ptah import view
from ptah.view.base import View
from ptah.view.resources import StaticView

from base import Base

abspath1, pkg1 = view.path('ptah.view.tests:static/dir1')
abspath2, pkg2 = view.path('ptah.view.tests:static/dir2')


class TestStaticManagement(Base):

    def _setup_ptah(self):
        pass

    def test_static_registration_errors(self):
        self.assertRaises(
            ValueError, view.static,
            'tests', 'ptah.view.tests:static/unknown---asdad')

        self.assertRaises(
            ValueError, view.static,
            'tests', 'ptah.view.tests:static/dir1/style.css')

    def test_static_register(self):
        view.static('tests', 'ptah.view.tests:static/dir1')
        self._init_ptah()

        request = self._makeRequest()
        self._setRequest(request)

        self.assertEquals(
            view.static_url(request, 'tests', 'styles.css'),
            'http://localhost:8080/static/tests/styles.css')

        self.assertEquals(
            view.static_url(request, 'tests'),
            'http://localhost:8080/static/tests')

    def test_static_register_url(self):
        from ptah.view import resources
        resources.STATIC.url = 'http://ptah.org/static'

        view.static('testsurl', 'ptah.view.tests:static/dir1')
        self._init_ptah()

        self.assertEquals(
            view.static_url(self.request, 'tests', 'styles.css'),
            'http://ptah.org/static/tests/styles.css')

    def test_static_buildtree(self):
        from ptah.view.resources import buildTree

        abspath, pkg = view.path('ptah.view.tests:static/dir2')
        self.assertEqual(buildTree(abspath),
                         {'style.css': 1, 'text.txt': 1})

        # do not include not allowed files
        abspath, pkg = view.path('ptah.view.tests:static/dir2')
        self.assertTrue('~test.html' not in buildTree(abspath))

        # subtrees
        abspath, pkg = view.path('ptah.view.tests:static')
        self.assertEqual(buildTree(abspath),
                         {os.path.join('dir1','style.css'): 1,
                          os.path.join('dir1','subdir','text.txt'): 1,
                          os.path.join('dir1','text2.txt'): 1,
                          os.path.join('dir2','style.css'): 1,
                          os.path.join('dir2','text.txt'): 1})

    def test_base_static_url(self):
        view.static('tests2', 'ptah.view.tests:static/dir1')
        self._init_ptah()

        request = self._makeRequest()

        base = View(None, request)

        self.assertEquals(
            base.static_url('tests2', 'styles.css'),
            'http://localhost:8080/static/tests2/styles.css')


class TestStaticView(Base):

    def test_resource_empty_pathinfo(self):
        environ = self._makeEnviron(PATH_INFO='')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '404 Not Found')

    def test_resource_doesnt_exist(self):
        environ = self._makeEnviron(PATH_INFO='/static/test/notthere')
        request = self._makeRequest(environ)

        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '404 Not Found')

    def test_resource_file(self):
        environ = self._makeEnviron(PATH_INFO='/static/test/style.css')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('/* CSS styles file 1 */' in response.body)

    def test_resource_file_from_subdir(self):
        environ = self._makeEnviron(PATH_INFO='/static/test/subdir/text.txt')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('test text 1' in response.body)

    def test_resource_file_with_cache(self):
        environ = self._makeEnviron(PATH_INFO='/static/test/style.css')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertIn('max-age=0', response.headers['Cache-Control'])

        from ptah.view import resources
        resources.STATIC.cache_max_age = 360

        response = inst(None, request)
        self.assertTrue(response.headers['Cache-Control'],
                        'public, max-age=360')

    def test_resource_layers_bypass_to_parent(self):
        # if not exist in upper layer tring to get from lower layer
        environ = self._makeEnviron(PATH_INFO='/static/test/text2.txt')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('text2 test 1' in response.body)

    def test_resource_layers_bypass_to_parent_subdir(self):
        # if not exist in upper layer tring to get from lower layer
        environ = self._makeEnviron(PATH_INFO='/static/test/subdir/text.txt')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('test text 1' in response.body)
