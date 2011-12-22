import ptah
from pyramid.view import render_view_to_response


class TestUriIntrospect(ptah.PtahTestCase):

    def test_uri_introspect(self):
        from ptah.manage.uri import ID_RESOLVER
        from ptah.manage.intr_renderers import UriRenderer

        def resolver(uri): # pragma: no cover
            return 'Resolved'

        self.config.ptah_uri_resolver('uri-intro-test', resolver)

        intr = self.registry.introspector.get(
            ID_RESOLVER, (ID_RESOLVER, 'uri-intro-test'))

        rendered = ptah.render_snippet(ID_RESOLVER, intr, self.request)

        self.assertIn('uri-intro-test', rendered)
        self.assertIn('ptah.manage.tests.test_intr_renderers', rendered)


class TestTypeIntrospect(ptah.PtahTestCase):

    def test_type_introspect(self):
        global Content1
        class Content1(ptah.cms.Content):
            __type__ = ptah.cms.Type('content1')

        self.config.scan(self.__class__.__module__)

        intr = self.registry.introspector.get(
            'ptah.cms:type', ('ptah.cms:type', 'content1'))

        res = ptah.render_snippet('ptah.cms:type', intr, self.request)
        self.assertIn('<small>cms-type:content1</small>', res)


class SubscribersIntrospect(ptah.PtahTestCase):

    def test_subscribers(self):
        from ptah.manage.introspect import IntrospectModule, Introspector

        mod = IntrospectModule(None, self.request)

        intr = mod['ptah.config:subscriber']

        res = render_view_to_response(intr, self.request)
        self.assertIn('Event subscribers', res.text)


class FieldIntrospect(ptah.PtahTestCase):

    def test_fields(self):
        from ptah.manage.introspect import IntrospectModule, Introspector

        mod = IntrospectModule(None, self.request)

        intr = mod['ptah.form:field']

        res = render_view_to_response(intr, self.request)
        self.assertIn('List of registered fields', res.text)
