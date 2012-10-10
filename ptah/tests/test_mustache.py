import os, tempfile, shutil, time
from zope.interface import implementedBy
from pyramid.compat import binary_type, text_type, text_
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationError, ConfigurationConflictError
from pyramid.httpexceptions import HTTPNotFound

import ptah
from ptah.testing import TestCase


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
            'test-bundle', 'ptah:tests/bundle/', i18n_domain='ptah')
        self.config.commit()

        data = self.registry.get(ID_BUNDLE)
        self.assertIn('test-bundle', data)

        intr = data['test-bundle']
        self.assertTrue(intr['abs_path'].endswith('tests/bundle/'))
        self.assertEqual(intr['i18n_domain'], 'ptah')

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
            '"test-bundle",["ptah","handlebars"],', res.text)
        self.assertIn(
            '"cat2":new ptah.Templates("cat2",{"form2"', res.text)

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
            '"test-bundle":"http://example.com/_mustache/test-bundle"',res.text)

    def test_build_bundle_toplevel_i18n(self):
        from ptah.mustache import bundle_view
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['mustache-langs'] = ['en','pt_BR']

        self.config.register_mustache_bundle(
            'test-bundle', 'ptah:tests/bundle2/', i18n_domain='ptah')
        self.request.matchdict['name'] = 'test-bundle'

        res = bundle_view(self.request)
        self.assertIn(
            "Handlebars.registerHelper('i18n-test-bundle'", res.text)
        self.assertIn(
            'ar bundle=new ptah.Templates("test-bundle",{"form"', res.text)
        self.assertIn('bundle.__i18n__ = {"Password":{"pt_BR":"Senha"}}',
                      res.text)


class TestBuildBundle(ptah.PtahTestCase):

    def setUp(self):
        super(TestBuildBundle, self).setUp()

        self.path = tempfile.mkdtemp()

        from ptah import mustache
        self.storage = self.registry.get(mustache.ID_BUNDLE)
        self._node_path = mustache.NODE_PATH

    def tearDown(self):
        super(TestBuildBundle, self).setUp()
        from ptah import mustache
        mustache.NODE_PATH = self._node_path

        shutil.rmtree(self.path)

    def test_no_nodejs(self):
        from ptah import mustache

        mustache.NODE_PATH = ''

        self.assertRaises(
            RuntimeError, mustache.build_hb_bundle,
            'ptah-templates', self.storage['ptah-templates'], self.registry)

    def test_compile_new(self):
        from ptah import mustache

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['amd-cache'] = self.path
        prefix = os.path.split(self.path)[-1]

        f = os.path.join(self.path, 'template')
        with open(f, 'w') as fn:
            fn.write('<div>{{test}}</div>')

        tmpl = text_type(mustache.compile_template(
            'test', f, mustache.NODE_PATH, self.path)[0])

        self.assertTrue(os.path.isfile(
                os.path.join(self.path, 'test-%s-template'%prefix)))
        self.assertTrue(os.path.isfile(
                os.path.join(self.path, 'test-%s-template.js'%prefix)))
        self.assertIn(
            'function (Handlebars,depth0,helpers,partials,data) {', tmpl)

    def test_compile_new_i18n(self):
        from ptah import mustache

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['amd-cache'] = self.path
        prefix = os.path.split(self.path)[-1]

        f = os.path.join(self.path, 'template')
        with open(f, 'w') as fn:
            fn.write('<div>{{test}}{{#i18n}}i18n text{{/i18n}}</div>')

        tmpl, i18n = mustache.compile_template(
            'test', f, mustache.NODE_PATH, self.path)
        tmpl = text_type(tmpl)

        self.assertIn('i18n text', i18n)
        self.assertTrue(os.path.isfile(
            os.path.join(self.path, 'test-%s-template.i18n'%prefix)))
        self.assertEqual(
            open(os.path.join(self.path,'test-%s-template'%prefix),'r').read(),
            '<div>{{test}}{{#i18n-test}}i18n text{{/i18n-test}}</div>')

    def test_compile_existing(self):
        from ptah import mustache

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['amd-cache'] = self.path
        prefix = os.path.split(self.path)[-1]

        f = os.path.join(self.path, 'template')
        with open(f, 'w') as fn:
            fn.write('<div>{{test}}</div>')

        time.sleep(0.01)

        f1 = os.path.join(self.path, 'test-%s-template'%prefix)
        with open(f1, 'w') as fn:
            fn.write('existing1')

        time.sleep(0.01)

        f2 = os.path.join(self.path, 'test-%s-template.js'%prefix)
        with open(f2, 'w') as fn:
            fn.write('existing2')

        tmpl = text_type(mustache.compile_template(
                'test', f, mustache.NODE_PATH, self.path)[0])

        self.assertEqual('existing2', tmpl)

    def test_compile_existing_i18n(self):
        """
        Skip compilation if it is compiled already
        """
        from ptah import mustache

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['amd-cache'] = self.path
        prefix = os.path.split(self.path)[-1]

        f = os.path.join(self.path, 'template')
        with open(f, 'w') as fn:
            fn.write('<div>{{test}}</div>')

        time.sleep(0.01)

        f1 = os.path.join(self.path, 'test-%s-template'%prefix)
        with open(f1, 'w') as fn:
            fn.write('existing1')

        time.sleep(0.01)

        f2 = os.path.join(self.path, 'test-%s-template.js'%prefix)
        with open(f2, 'w') as fn:
            fn.write('existing2')

        time.sleep(0.01)

        f1 = os.path.join(self.path, 'test-%s-template.i18n'%prefix)
        with open(f1, 'w') as fn:
            fn.write('["existing3"]')

        tmpl,i18n = mustache.compile_template(
                'test', f, mustache.NODE_PATH, self.path)

        self.assertEqual(['existing3'], i18n)


class TextExtractI18N(TestCase):

    def test_extract(self):
        from pyramid.compat import NativeIO
        from ptah.mustache import extract_i18n_mustache

        f = NativeIO('<div>{{#i18n}}Test \n message{{/i18n}}</div>')

        d = extract_i18n_mustache(f, [], [], [])
        self.assertEqual(d[0], (5, None, text_type('Test \n message'), []))
