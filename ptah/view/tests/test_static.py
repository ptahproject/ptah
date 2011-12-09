""" test for static assets api """
import os.path
import ptah
from ptah import view
from ptah.testing import PtahTestCase
from ptah.view.base import View
from ptah.view.resources import StaticView

#abspath1, pkg1 = view.path('ptah.view.tests:static/dir1')
#abspath2, pkg2 = view.path('ptah.view.tests:static/dir2')


class TestStaticManagement(PtahTestCase):

    _init_ptah = False

    def test_static_registration_errors(self):
        self.assertRaises(
            ValueError, view.static,
            'tests', 'ptah.view.tests:static/unknown---asdad')

        self.assertRaises(
            ValueError, view.static,
            'tests', 'ptah.view.tests:static/dir1/style.css')

    def test_static_register(self):
        view.static('tests', 'ptah.view.tests:static/dir1')
        self.init_ptah()

        self.assertEquals(
            view.static_url(self.request, 'tests', 'styles.css'),
            'http://example.com/static/tests/styles.css')

        self.assertEquals(
            view.static_url(self.request, 'tests'),
            'http://example.com/static/tests')

    def test_static_register_url(self):
        view.static('testsurl', 'ptah.view.tests:static/dir1')

        self.registry.settings['ptah.static_url'] = 'http://ptah.org/static'
        self.init_ptah()

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
        self.init_ptah()

        base = View(None, self.request)

        self.assertEquals(
            base.static_url('tests2', 'styles.css'),
            'http://example.com/static/tests2/styles.css')


class TestStaticView(PtahTestCase):

    def test_resource_empty_pathinfo(self):
        request = self.make_request(
            environ={'PATH_INFO': ''})
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '404 Not Found')

    def test_resource_doesnt_exist(self):
        request = self.make_request(
            environ = {'PATH_INFO': '/static/test/notthere'})

        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '404 Not Found')

    def test_resource_file(self):
        request = self.make_request(
            environ={'PATH_INFO': '/static/test/style.css'})
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('/* CSS styles file 1 */' in \
                        response.body.decode('utf-8'))

    def test_resource_file_from_subdir(self):
        request = self.make_request(
            environ={'PATH_INFO': '/static/test/subdir/text.txt'})
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('test text 1' in response.body.decode('utf-8'))

    def test_resource_file_with_cache(self):
        request = self.make_request(
            environ={'PATH_INFO': '/static/test/style.css'})
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertIn('max-age=0', response.headers['Cache-Control'])

        STATIC = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        STATIC.cache_max_age = 360

        response = inst(None, request)
        self.assertTrue(response.headers['Cache-Control'],
                        'public, max-age=360')

    def test_resource_layers_bypass_to_parent(self):
        # if not exist in upper layer tring to get from lower layer
        request = self.make_request(
            environ={'PATH_INFO':'/static/test/text2.txt'})
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('text2 test 1' in response.body.decode('utf-8'))

    def test_resource_layers_bypass_to_parent_subdir(self):
        # if not exist in upper layer tring to get from lower layer
        request = self.make_request(
            environ={'PATH_INFO': '/static/test/subdir/text.txt'})
        inst = StaticView(abspath1, 'static/test')

        response = inst(None, request)
        self.assertTrue(response.status == '200 OK')
        self.assertTrue('test text 1' in response.body.decode('utf-8'))
