""" test for static assets api """
import unittest, os.path
from memphis import config, view
from memphis.view import resources
from memphis.view.base import View
from memphis.view.resources import buildTree
from memphis.view.resources import StaticView

from base import Base

abspath1, pkg1 = view.path('memphis.view.tests:static/dir1')
abspath2, pkg2 = view.path('memphis.view.tests:static/dir2')
dirinfo1 = buildTree(abspath1)
dirinfo2 = buildTree(abspath2)


class TestStaticManagement(Base):

    def _setup_memphis(self):
        pass

    def test_static_registration_errors(self):
        self.assertRaises(
            ValueError, view.static,
            'tests', 'memphis.view.tests:static/unknown---asdad')

        self.assertRaises(
            ValueError, view.static,
            'tests', 'memphis.view.tests:static/dir1/style.css')

    def test_static_register(self):
        view.static('tests', 'memphis.view.tests:static/dir1')
        self._init_memphis()

        request = self._makeRequest()
        self._setRequest(request)

        self.assertEquals(
            view.static_url('tests', 'styles.css', request),
            'http://localhost:8080/static/tests/styles.css')

        self.assertEquals(
            view.static_url('tests', '', request),
            'http://localhost:8080/static/tests')

    def test_static_register_url(self):
        from memphis.view import resources
        resources.STATIC.url = 'http://memphis.org/static'

        view.static('testsurl', 'memphis.view.tests:static/dir1')
        self._init_memphis()

        self.assertEquals(
            view.static_url('tests', 'styles.css', self.request),
            'http://memphis.org/static/tests/styles.css')

    def test_static_buildtree(self):
        from memphis.view.resources import buildTree

        abspath, pkg = view.path('memphis.view.tests:static/dir2')
        self.assertEqual(buildTree(abspath),
                         {'style.css': 1, 'text.txt': 1})

        # do not include not allowed files
        abspath, pkg = view.path('memphis.view.tests:static/dir2')
        self.assertTrue('~test.html' not in buildTree(abspath))

        # subtrees
        abspath, pkg = view.path('memphis.view.tests:static')
        self.assertEqual(buildTree(abspath),
                         {os.path.join('dir1','style.css'): 1,
                          os.path.join('dir1','subdir','text.txt'): 1,
                          os.path.join('dir1','text2.txt'): 1,
                          os.path.join('dir2','style.css'): 1,
                          os.path.join('dir2','text.txt'): 1})

    def test_base_static_url(self):
        view.static('tests2', 'memphis.view.tests:static/dir1')
        self._init_memphis()

        request = self._makeRequest()

        base = View(None, request)

        self.assertEquals(
            base.static_url('tests2', 'styles.css'),
            'http://localhost:8080/static/tests2/styles.css')

    def test_static_wired(self):
        # something strange can happen, info can be removed
        # from registry before memphis init (tests for example)
        view.static('tests', 'memphis.view.tests:static/dir1')

        self.assertTrue('tests' in resources.registry)

        del resources.registry['tests']
        self._init_memphis()

        self.assertTrue('tests' in resources.registry)


class TestStaticView(Base):

    def test_resource_empty_pathinfo(self):
        environ = self._makeEnviron(PATH_INFO='')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, dirinfo1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '404 Not Found')
        self.assertTrue(
            'The resource at http://localhost:8080 could not be found'
            in response.body)

    def test_resource_doesnt_exist(self):
        environ = self._makeEnviron(PATH_INFO='/static/test/notthere')
        request = self._makeRequest(environ)

        inst = StaticView(abspath1, dirinfo1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '404 Not Found')
        self.assertTrue(
            'http://localhost:8080/static/test/notthere' in response.body)

    def test_resource_file(self):
        environ = self._makeEnviron(PATH_INFO='/static/test/style.css')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, dirinfo1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('/* CSS styles file 1 */' in response.body)

    def test_resource_file_from_subdir(self):
        environ = self._makeEnviron(PATH_INFO='/static/test/subdir/text.txt')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, dirinfo1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('test text 1' in response.body)

    def test_resource_file_with_cache(self):
        environ = self._makeEnviron(PATH_INFO='/static/test/style.css')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, dirinfo1, 'static/test')

        response = inst(None, request)
        self.assertFalse('Cache-Control' in response.headers)

        from memphis.view import resources
        resources.STATIC.cache_max_age = 360

        response = inst(None, request)
        self.assertTrue(response.headers['Cache-Control'],
                        'public, max-age=360')

    def test_resource_layers_bypass_to_parent(self):
        # if not exist in upper layer tring to get from lower layer
        environ = self._makeEnviron(PATH_INFO='/static/test/text2.txt')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, dirinfo1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('text2 test 1' in response.body)

    def test_resource_layers_bypass_to_parent_subdir(self):
        # if not exist in upper layer tring to get from lower layer
        environ = self._makeEnviron(PATH_INFO='/static/test/subdir/text.txt')
        request = self._makeRequest(environ)
        inst = StaticView(abspath1, dirinfo1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('test text 1' in response.body)
