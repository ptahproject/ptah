import ptah
from ptah.testing import PtahTestCase
from pyramid.view import render_view_to_response
from pyramid.testing import DummyRequest


class TestIntrospectModule(PtahTestCase):

    _init_ptah = False

    def test_introspect_module(self):
        self.init_ptah()

        from ptah.manage.manage import PtahManageRoute
        from ptah.manage.introspect import IntrospectModule

        request = self.make_request()

        ptah.auth_service.set_userid('test')
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['managers'] = ('*',)

        mr = PtahManageRoute(request)
        mod = mr['introspect']

        self.assertIsInstance(mod, IntrospectModule)

    def test_traversable(self):
        from ptah.manage.introspect import IntrospectModule, Introspector
        self.init_ptah()

        request = self.make_request()
        mod = IntrospectModule(None, request)

        self.assertRaises(KeyError, mod.__getitem__, 'unknown')

        package = mod['ptah:resolver']
        self.assertIsInstance(package, Introspector)

    def test_view(self):
        from ptah.manage.introspect import IntrospectModule, Introspector
        self.init_ptah()

        request = self.make_request()
        mod = IntrospectModule(None, request)

        res = render_view_to_response(mod, request)
        self.assertIn('ptah:resolver', res.text)
        self.assertIn(
          '<a href="http://example.com/ptah-manage/introspect/ptah:resolver/">',
          res.text)

    def test_intr_view(self):
        from ptah.manage.introspect import IntrospectModule, Introspector
        self.init_ptah()

        request = self.make_request()
        mod = IntrospectModule(None, request)

        intr = mod['ptah:resolver']

        res = render_view_to_response(intr, request)
        self.assertIn('System super user', res.text)

    def test_intr_view_default(self):
        from ptah.manage.introspect import IntrospectModule, Introspector
        self.init_ptah()

        request = self.make_request()
        mod = IntrospectModule(None, request)

        intr = mod['ptah.form:field-preview']

        res = render_view_to_response(intr, request)
        self.assertIn('ptah.form:field-preview', res.text)
