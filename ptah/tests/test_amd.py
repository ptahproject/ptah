import os, tempfile
import ptah
from pyramid.path import AssetResolver
from pyramid.config import Configurator
from pyramid.compat import binary_type, text_type, bytes_
from pyramid.response import FileResponse
from pyramid.exceptions import ConfigurationError, ConfigurationConflictError
from pyramid.httpexceptions import HTTPNotFound


class TestAmdDirective(ptah.PtahTestCase):

    _init_ptah = False

    def test_amd_directive(self):
        self.assertFalse(hasattr(self.config, 'register_amd_module'))
        self.config.include('ptah')

        self.assertTrue(hasattr(self.config, 'register_amd_module'))


class TestAmd(ptah.PtahTestCase):

    _auto_commit = False

    def test_amd_registration(self):
        from ptah.amd import ID_AMD_MODULE

        self.config.register_amd_module(
            'test', 'ptah:tests/dir/test.js')
        self.config.commit()

        data = self.registry.get(ID_AMD_MODULE)
        self.assertIn('test', data)
        self.assertEqual(data['test']['path'], 'ptah:tests/dir/test.js')

    def test_amd_registration_with_require(self):
        from ptah.amd import ID_AMD_MODULE

        self.config.register_amd_module(
            'test', 'ptah:tests/dir/test.js', require='test2')
        self.config.commit()

        data = self.registry.get(ID_AMD_MODULE)
        self.assertEqual(data['test']['require'], ('test2',))

    def test_reg_conflict(self):
        self.init_ptah()

        self.config.register_amd_module(
            'test', 'ptah:tests/dir/test1.js')
        self.config.register_amd_module(
            'test', 'ptah:tests/dir/test2.js')

        self.assertRaises(
            ConfigurationConflictError, self.config.commit)

    def test_amd_dir(self):
        from ptah.amd import ID_AMD_MODULE

        self.config.register_amd_dir('ptah:tests/dir/')
        self.config.commit()

        data = self.registry.get(ID_AMD_MODULE)
        self.assertEqual(data['jca-globals']['path'], 'ptah:tests/dir/test.js')


class TestAmdSpec(ptah.PtahTestCase):

    def test_unknown_spec(self):
        from ptah.amd import amd_spec, ID_AMD_SPEC

        self.request.matchdict['name'] = 'test.js'
        self.request.matchdict['specname'] = 'test'

        self.assertIsInstance(amd_spec(self.request), HTTPNotFound)

    def test_spec_without_path(self):
        from ptah.amd import amd_spec, ID_AMD_SPEC

        self.request.matchdict['name'] = 'test.js'
        self.request.matchdict['specname'] = 'test'

        self.registry[ID_AMD_SPEC] = {'test': {'test.js': {'url':'http://...'}}}
        self.assertIsInstance(amd_spec(self.request), HTTPNotFound)

    def test_spec(self):
        from ptah.amd import amd_spec, ID_AMD_SPEC

        self.request.matchdict['name'] = 'test.js'
        self.request.matchdict['specname'] = 'test'

        resolver = AssetResolver()
        path = resolver.resolve('ptah:tests/dir/test.js').abspath()

        self.registry[ID_AMD_SPEC] = {'test': {'test.js': {'path':path}}}
        self.assertIsInstance(amd_spec(self.request), FileResponse)


class TestAmdInit(ptah.PtahTestCase):

    def setUp(self):
        super(TestAmdInit, self).setUp()

        self.config.add_static_view('_tests', 'ptah:tests/dir/')

    def test_amd_init_no_spec(self):
        from ptah.amd import amd_init

        self.config.register_amd_module(
            'test-mod', 'ptah:tests/dir/test.js')

        self.request.matchdict['specname'] = 'unknown'

        resp = amd_init(self.request)
        self.assertIsInstance(resp, HTTPNotFound)

    def test_amd_init_with_spec_url(self):
        from ptah.amd import amd_init, ID_AMD_MODULE, ID_AMD_SPEC

        self.registry[ID_AMD_MODULE] = {'ptah': {'path':'ptah:static/ptah.js'}}
        self.registry[ID_AMD_SPEC] = \
            {'test': {'ptah': {'url': 'http://test.com/example.js'}}}

        self.request.matchdict['specname'] = 'test'

        resp = amd_init(self.request)
        self.assertEqual(resp.status, '200 OK')

        self.registry[ID_AMD_SPEC] = \
            {'test': {'ptah': {'name':'test', 'path':'ptah:static/example.js'}}}
        resp = amd_init(self.request)
        self.assertIn('"ptah": "http://example.com/_amd_test/t"', resp.text)

    def test_amd_init_with_spec_mustache(self):
        from ptah.amd import amd_init, ID_AMD_MODULE, ID_AMD_SPEC

        self.request.matchdict['specname'] = 'test'
        self.registry[ID_AMD_SPEC] = \
            {'test': {'ptah-templates':
                      {'name':'test', 'path':'ptah:static/example.js'}}}
        resp = amd_init(self.request)
        self.assertIn(
            '"ptah-templates":"http://example.com/_amd_test/t"', resp.text)

    def test_amd_mod_paths(self):
        from ptah.amd import amd_init

        self.config.register_amd_module(
            'test-mod', 'ptah:tests/dir/test.js')

        self.request.matchdict['specname'] = '_'

        resp = amd_init(self.request)
        self.assertIn('var ptah_amd_modules = {', resp.text)
        self.assertIn(
            '"test-mod": "http://example.com/_tests/test"', resp.text)


class TestInitAmdSpec(ptah.PtahTestCase):

    def setUp(self):
        self._files = []
        super(TestInitAmdSpec, self).setUp()

    def _create_file(self, text):
        d, fn = tempfile.mkstemp()
        self._files.append(fn)
        with open(fn, 'wb') as f:
            f.write(bytes_(text, 'utf-8'))

        return fn

    def tearDown(self):
        for f in self._files:
            os.unlink(f)

        super(TestInitAmdSpec, self).tearDown()

    def test_empty_spec(self):
        fn = self._create_file("[test.js]\nmodules = lib1")

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['amd-spec'] = ''

        from ptah.amd import init_amd_spec, ID_AMD_SPEC

        # no amd-spec-dir
        init_amd_spec(self.config)

        storage = self.registry[ID_AMD_SPEC]
        self.assertEqual(storage, {})

    def test_empty_dir(self):
        fn = self._create_file("[test.js]\nmodules = lib1")

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['amd-spec'] = ['%s'%fn, 'test:%s'%fn]

        from ptah.amd import init_amd_spec, ID_AMD_SPEC

        # no amd-spec-dir
        self.assertRaises(ConfigurationError, init_amd_spec, self.config)

    def test_simple(self):
        fn = self._create_file("[test.js]\nmodules = lib1")

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['amd-spec'] = ['%s'%fn, 'test:%s'%fn]
        cfg['amd-dir'] = '/test'

        from ptah.amd import init_amd_spec, ID_AMD_SPEC
        init_amd_spec(self.config)

        storage = self.registry[ID_AMD_SPEC]
        self.assertIn('', storage)
        self.assertTrue(storage['']['test.js']['path'].endswith('/test.js'))
        self.assertIn('test', storage)

    def test_bundle_with_url(self):
        fn = self._create_file(
            "[test.js]\nurl=http://example.com/test.js\nmodules = lib1")

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['amd-spec'] = [fn]
        cfg['amd-dir'] = '/test'

        from ptah.amd import init_amd_spec, ID_AMD_SPEC
        init_amd_spec(self.config)

        storage = self.registry[ID_AMD_SPEC]
        self.assertIn('url', storage['']['test.js'])
        self.assertEqual(storage['']['test.js']['url'],
                         'http://example.com/test.js')

    text1 = """
[test.js]
modules = lib1

[test.js]
modules = lib2
"""

    def test_multple_bundles(self):
        fn = self._create_file(self.text1)

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['amd-spec'] = ['test:%s'%fn, 'test:%s'%fn]
        cfg['amd-dir'] = '/unknown'

        from ptah.amd import init_amd_spec
        self.assertRaises(ConfigurationError, init_amd_spec, self.config)


class TestRequestRenderers(ptah.PtahTestCase):

    def setUp(self):
        super(TestRequestRenderers, self).setUp()

        self.cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)

        from pyramid.interfaces import IRequestExtensions
        extensions = self.registry.getUtility(IRequestExtensions)
        self.request._set_extensions(extensions)

    def make_request(self):
        from pyramid.request import Request
        return Request(environ=self._environ)

    def test_render_amd_container(self):
        text = self.request.render_amd_container('app', attr='123')

        self.assertEqual(
            text, '<div ptah="app" data-attr="123"></div>')

    def test_render_amd_includes(self):
        self.cfg['amd-enabled'] = False

        text = self.request.render_amd_includes().strip()
        self.assertEqual(
            text, '<script src="http://example.com/_ptah/static/lib/curl.js"> </script>\n<script src="http://example.com/_amd__.js"> </script>\n<script>curl([\'domReady!\']).next([\'ptah\'], function(ptah) {ptah.init(ptah_amd_modules)})</script>')

        text = self.request.render_amd_includes('test-spec').strip()
        self.assertIn(
            '<script src="http://example.com/_amd__.js"> </script>', text)

    def test_render_amd_includes_no_init(self):
        self.cfg['amd-enabled'] = False

        text = self.request.render_amd_includes(init=False).strip()
        self.assertEqual(
            text, '<script src="http://example.com/_ptah/static/lib/curl.js"> </script>\n<script src="http://example.com/_amd__.js"> </script>')

    def test_render_amd_includes_unknown_spec(self):
        self.cfg['amd-enabled'] = True

        self.assertRaises(
            RuntimeError, self.request.render_amd_includes, 'unknown')
        self.assertRaises(
            RuntimeError, self.request.render_amd_includes, 'spec')

    def test_render_amd_includes_default(self):
        self.cfg['amd-enabled'] = True

        text = self.request.render_amd_includes().strip()
        self.assertEqual(
            text, '<script src="http://example.com/_ptah/static/lib/curl.js"> </script>\n<script src="http://example.com/_amd__.js"> </script>\n<script>curl([\'domReady!\']).next([\'ptah\'], function(ptah) {ptah.init(ptah_amd_modules)})</script>')

    def test_render_amd_includes_spec(self):
        from ptah.amd import ID_AMD_SPEC

        self.cfg['amd-enabled'] = True

        self.registry[ID_AMD_SPEC] = {'test':
                                      {'test.js': {'path':'/test/test.js'}}}

        text = self.request.render_amd_includes('test').strip()
        self.assertIn(
            '<script src="http://example.com/_amd_test.js"> </script>', text)

        text = self.request.render_amd_includes('test', 'test').strip()
        self.assertIn(
            '<script src="http://example.com/_amd_test.js"> </script>\n<script src="http://example.com/_amd_test/test.js"></script>', text)
