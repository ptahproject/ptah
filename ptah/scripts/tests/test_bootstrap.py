import unittest
from pyramid.registry import Registry


class Test_bootstrap(unittest.TestCase):

    def setUp(self):
        import ptah.scripts
        import pyramid.paster
        self.original_get_app = ptah.scripts.get_app
        self.original_global_registries = ptah.scripts.global_registries

        self.app = app = object()
        self.registry = registry = Registry()

        class DummyGetApp(object):

            last = registry

            def __call__(self, *a, **kw):
                self.a = a
                self.kw = kw
                return app

        pyramid.paster.get_app = DummyGetApp()
        ptah.scripts.global_registries = DummyGetApp()

    def tearDown(self):
        import ptah.scripts
        import pyramid.paster
        pyramid.paster.get_app = self.original_get_app
        ptah.scripts.global_registries = self.original_global_registries

    def test_boostrap(self):
        import ptah
        from ptah.scripts import bootstrap

        result = bootstrap('/foo/settings.ini')

        self.assertEqual(result['app'], self.app)
        self.assertEqual(result['registry'], self.registry)
        self.assertTrue(result['request'] is not None)
        self.assertEqual(result['request'].registry, self.registry)
        self.assertFalse(ptah.POPULATE)
