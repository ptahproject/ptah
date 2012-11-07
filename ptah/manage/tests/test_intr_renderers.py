import ptah
from pyramid.view import render_view_to_response


class TestUriIntrospect(ptah.PtahTestCase):

    def test_uri_introspect(self):
        from ptah.manage.uri import ID_RESOLVER

        def resolver(uri): # pragma: no cover
            return 'Resolved'

        self.config.ptah_uri_resolver('uri-intro-test', resolver)

        intr = self.registry.introspector.get(
            ID_RESOLVER, (ID_RESOLVER, 'uri-intro-test'))

        rendered = self.request.render_tmpl(
            'ptah-intr:ptah-uriresolver', intr,
            manage_url='/ptah-manage', rst_to_html=ptah.rst_to_html)

        self.assertIn('uri-intro-test', rendered)
        self.assertIn('test_intr_renderers', rendered)


class SubscribersIntrospect(ptah.PtahTestCase):

    def test_subscribers(self):
        from ptah.manage.introspect import IntrospectModule

        mod = IntrospectModule(None, self.request)

        intr = mod['ptah:subscriber']

        res = render_view_to_response(intr, self.request)
        self.assertIn('ptah:subscriber', res.text)


class FieldIntrospect(ptah.PtahTestCase):

    def test_fields(self):
        from ptah.manage.introspect import IntrospectModule

        mod = IntrospectModule(None, self.request)

        intr = mod['pform:field']

        res = render_view_to_response(intr, self.request)
        self.assertIn('pform:field', res.text)
