from zope.interface import implementedBy
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationError, ConfigurationConflictError
from pyramid.httpexceptions import HTTPNotFound

import ptah


class TestBundleDirective(ptah.PtahTestCase):

    _init_ptah = False

    def test_amd_directive(self):
        self.assertFalse(hasattr(self.config, 'register_mustache_bundle'))
        self.config.include('ptah')

        self.assertTrue(hasattr(self.config, 'register_mustache_bundle'))


class TestBundleReg(ptah.PtahTestCase):

    _auto_commit = False

    def test_bundle_registration(self):
        from ptah.mustache import ID_BUNDLE

        self.config.register_mustache_bundle(
            'test-bundle', 'ptah:tests/bundle/')
        self.config.commit()

        data = self.registry.get(ID_BUNDLE)
        self.assertIn('test-bundle', data)

        intr = data['test-bundle']
        self.assertTrue(intr['abs_path'].endswith('tests/bundle/'))

    def test_bundle_unknown(self):
        self.assertRaises(
            ConfigurationError,
            self.config.register_mustache_bundle,
            'test-bundle', 'ptah:tests/unknown/')

    def test_bundle_empty_path(self):
        self.assertRaises(
            ConfigurationError,
            self.config.register_mustache_bundle, 'test-bundle')

    def test_bundle_not_dir(self):
        self.assertRaises(
            ConfigurationError,
            self.config.register_mustache_bundle,
            'test-bundle', 'ptah:tests/bundle/cat1/form.mustache')

    def test_bundle_conflict(self):
        self.config.register_mustache_bundle(
            'test-bundle', 'ptah:tests/bundle/')
        self.config.register_mustache_bundle(
            'test-bundle', 'ptah:tests/bundle/')

        self.assertRaises(
            ConfigurationConflictError, self.config.commit)


class TestBundleRoute(ptah.PtahTestCase):

    def test_unknown_bundle(self):
        from ptah.mustache import bundle_view

        self.request.matchdict['name'] = 'unknown'

        res = bundle_view(self.request)
        self.assertIsInstance(res, HTTPNotFound)

    def test_route(self):
        from ptah.mustache import bundle_view

        self.config.register_mustache_bundle(
            'test-bundle', 'ptah:tests/bundle/')
        self.request.matchdict['name'] = 'test-bundle'

        res = bundle_view(self.request)
        self.assertIn(
            '"test-bundle",["ptah","handlebars"],', res.body)
        self.assertIn(
            '"cat2":new ptah.Templates("cat2",{"form2"', res.body)

    def test_list_bundles(self):
        from ptah.mustache import list_bundles

        self.config.register_mustache_bundle(
            'test-bundle', 'ptah:tests/bundle/')

        self.assertIn(
            ('test-bundle',
             'http://example.com/_mustache/test-bundle.js'),
            list_bundles(self.request))

    def test_list_bundles_unset(self):
        from ptah.mustache import list_bundles

        config = Configurator()
        request = self.make_request()
        request.registry = config.registry

        self.assertEqual(list_bundles(request), [])

    def test_bundles_amd(self):
        from ptah.amd import amd_init

        self.config.register_mustache_bundle(
            'test-bundle', 'ptah:tests/bundle/')

        self.request.matchdict['specname'] = '_'

        res = amd_init(self.request)
        self.assertIn(
            '"test-bundle":"http://example.com/_mustache/test-bundle"',res.body)
