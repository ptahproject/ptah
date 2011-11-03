import ptah
from ptah import config, view
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from base import Base


class TestExceptions(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestExceptions, self).tearDown()

    def test_not_found(self):
        from ptah.exc import NotFound
        self._init_ptah()

        class Context(object):
            """ """

        request = DummyRequest()
        request.root = Context()

        excview = NotFound(HTTPNotFound(), request)
        excview.update()

        self.assertIs(excview.__parent__, request.root)
        self.assertEqual(request.response.status, '404 Not Found')

    def test_forbidden(self):
        from ptah.exc import Forbidden
        self._init_ptah()

        class Context(object):
            """ """

        request = DummyRequest()
        request.url = u'http://example.com'
        request.application_url = u'http://example.com'
        request.root = Context()

        excview = Forbidden(HTTPForbidden(), request)
        excview.update()

        res = request.response

        self.assertIs(excview.__parent__, request.root)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(
            res.headers['location'],
            'http://example.com/login.html?came_from=http%3A%2F%2Fexample.com')

    def test_forbidden_default_root(self):
        from ptah.exc import Forbidden
        from pyramid.interfaces import IRootFactory

        class Root(object):
            """ """
            def __init__(self, request):
                self.request = request

        request = DummyRequest()
        request.url = u'http://example.com'
        request.application_url = u'http://example.com'

        config.registry.registerUtility(Root, IRootFactory)

        excview = Forbidden(HTTPForbidden(), request)
        excview.update()

        self.assertIs(excview.__parent__, request.root)
        self.assertIsInstance(request.root, Root)

    def test_forbidden_user(self):
        from ptah.exc import Forbidden
        self._init_ptah()
        config.start(self.p_config)

        class Context(object):
            """ """
            __name__ = 'test'

        request = DummyRequest()
        request.root = Context()
        ptah.authService.set_userid('user')

        res = Forbidden.__renderer__(HTTPForbidden(), request)
        self.assertEqual(res.status, '403 Forbidden')

    def test_forbidden_custom_login(self):
        from ptah.exc import Forbidden

        class Context(object):
            """ """

        request = DummyRequest()
        request.url = u'http://example.com'
        request.root = Context()
        ptah.PTAH_CONFIG.login = '/custom-login.html'

        excview = Forbidden(HTTPForbidden(), request)
        excview.update()

        res = request.response

        self.assertIs(excview.__parent__, request.root)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(
            res.headers['location'],
            'http://example.com/custom-login.html?came_from=http%3A%2F%2Fexample.com')

    def test_forbidden_custom_login_domain(self):
        from ptah.exc import Forbidden

        class Context(object):
            """ """

        request = DummyRequest()
        request.url = u'http://example.com'
        request.root = Context()
        ptah.PTAH_CONFIG.login = 'http://login.example.com'

        excview = Forbidden(HTTPForbidden(), request)
        excview.update()

        res = request.response

        self.assertIs(excview.__parent__, request.root)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(
            res.headers['location'],
            'http://login.example.com?came_from=http%3A%2F%2Fexample.com')
