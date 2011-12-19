import ptah


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
