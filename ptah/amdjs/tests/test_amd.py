import os
import tempfile
import mock
from pyramid.path import AssetResolver
from pyramid.compat import bytes_
from pyramid.config import Configurator
from pyramid.response import FileResponse
from pyramid.exceptions import ConfigurationError, ConfigurationConflictError
from pyramid.httpexceptions import HTTPNotFound

from ptah.testing import PtahTestCase, TestCase


class TestAmdDirective(PtahTestCase):

    _include = False
    _init_ptah = False

    def test_amd_directive(self):
        self.assertFalse(hasattr(self.config, 'add_amd_dir'))
        self.assertFalse(hasattr(self.config, 'add_amd_js'))
        self.assertFalse(hasattr(self.config, 'add_amd_css'))
        self.config.include('ptah.amdjs')

        self.assertTrue(hasattr(self.config, 'add_amd_dir'))
        self.assertTrue(hasattr(self.config, 'add_amd_js'))
        self.assertTrue(hasattr(self.config, 'add_amd_css'))


class TestAmd(PtahTestCase):

    _auto_commit = False
    _init_ptah = False
    _settings = {'amd.debug': 'f'}

    def test_js_registration(self):
        from ptah.amdjs.amd import ID_AMD_MODULE, JS_MOD

        self.config.add_amd_js(
            'test', 'ptah.amdjs:tests/dir/test.js')
        self.config.commit()

        data = self.registry.get(ID_AMD_MODULE)
        self.assertIn('test', data)
        self.assertEqual(data['test']['path'],
                         'ptah.amdjs:tests/dir/test.js')
        self.assertEqual(data['test']['tp'], JS_MOD)

    def test_css_registration(self):
        from ptah.amdjs.amd import ID_AMD_MODULE, CSS_MOD

        self.config.add_amd_css(
            'test', 'ptah.amdjs:tests/dir/test3.css')
        self.config.commit()

        data = self.registry.get(ID_AMD_MODULE)
        self.assertIn('test', data)
        self.assertEqual(data['test']['path'],
                         'ptah.amdjs:tests/dir/test3.css')
        self.assertEqual(data['test']['tp'], CSS_MOD)

    def test_js_registration_with_require(self):
        from ptah.amdjs.amd import ID_AMD_MODULE

        self.config.add_amd_js(
            'test', 'ptah.amdjs:tests/dir/test.js', requires='test2')
        self.config.commit()

        data = self.registry.get(ID_AMD_MODULE)
        self.assertEqual(data['test']['requires'], ('test2',))

    def test_reg_conflict(self):
        self.config.commit()

        self.config.add_amd_js(
            'test', 'ptah.amdjs:tests/dir/test.js')
        self.config.add_amd_js(
            'test', 'ptah.amdjs:tests/dir/test2.js')

        self.assertRaises(
            ConfigurationConflictError, self.config.commit)

    def test_amd_dir(self):
        from ptah.amdjs.amd import ID_AMD_MODULE, CSS_MOD

        self.config.add_amd_dir('ptah.amdjs:tests/dir/')
        self.config.commit()

        data = self.registry.get(ID_AMD_MODULE)
        self.assertEqual(data['jca-globals']['path'],
                         'ptah.amdjs:tests/dir/test.js')
        self.assertEqual(data['test3.css']['path'],
                         'ptah.amdjs:tests/dir/test3.css')
        self.assertEqual(data['test3.css']['tp'], CSS_MOD)


class TestAmdInit(PtahTestCase):

    _init_ptah = False
    _settings = {'amd.debug': 'f'}

    def setUp(self):
        super(TestAmdInit, self).setUp()

        self.registry.settings['amd.enabled'] = True
        self.config.add_static_view('_tests', 'ptah.amdjs:tests/dir/')

    @mock.patch('ptah.amdjs.amd.build_init')
    def test_build_md5(self, m_binit):
        from ptah.amdjs.amd import build_md5

        m_binit.return_value = '123'
        h = build_md5(self.request, '_')
        self.assertEqual('202cb962ac59075b964b07152d234b70', h)
        self.assertTrue(m_binit.called)

    @mock.patch('ptah.amdjs.amd.build_init')
    def test_build_md5_cached(self, m_binit):
        from ptah.amdjs.amd import build_md5, ID_AMD_MD5

        self.registry[ID_AMD_MD5]['_'] = '123'

        h = build_md5(self.request, '_')
        self.assertEqual('123', h)
        self.assertFalse(m_binit.called)

    def test_amd_init_no_spec(self):
        from ptah.amdjs.amd import amd_init

        self.config.add_amd_js(
            'test-mod', 'ptah.amdjs:tests/dir/test.js')

        self.request.matchdict['specname'] = 'unknown'

        resp = amd_init(self.request)
        self.assertIsInstance(resp, HTTPNotFound)

    def test_amd_init_with_v(self):
        from ptah.amdjs.amd import amd_init, ID_AMD_SPEC

        self.request.params['_v'] = '123'
        self.request.matchdict['specname'] = 'test'

        self.registry[ID_AMD_SPEC] = \
            {'test': {'pyramid': {'name': 'test',
                                  'md5': '123',
                                  'path': 'ptah.amdjs:static/example.js'}}}

        resp = amd_init(self.request)
        self.assertEqual('max-age=31536000', resp.headers['Cache-Control'])
        self.assertIn(
            '"pyramid": "/_amdjs/static/example.js?_v=123"', resp.text)

    def test_amd_init_from_file(self):
        from ptah.amdjs.amd import amd_init, RESOLVER, ID_AMD_SPEC

        self.request.params['_v'] = '123'
        self.request.matchdict['specname'] = 'test'

        self.registry[ID_AMD_SPEC] = \
            {'test': {'pyramid': {}},
             'test-init': RESOLVER.resolve(
                 'ptah.amdjs:tests/dir/test2.js').abspath()}

        resp = amd_init(self.request)
        self.assertIsInstance(resp, FileResponse)
        self.assertEqual('max-age=31536000', resp.headers['Cache-Control'])

    def test_amd_init_with_spec_handlebars(self):
        from ptah.amdjs.amd import amd_init, ID_AMD_SPEC

        self.request.matchdict['specname'] = 'test'
        self.request.registry = self.registry
        self.registry[ID_AMD_SPEC] = {
            'test': {'underscore':
                     {'name': 'test',
                      'md5': '123',
                      'path': 'ptah.amdjs:static/example.js'}}
        }
        resp = amd_init(self.request)
        self.assertIn(
            '"underscore": "/_amdjs/static/example.js?_v=123"', resp.text)

    def test_amd_mod_paths(self):
        from ptah.amdjs.amd import amd_init

        self.config.add_amd_js(
            'test-mod', 'ptah.amdjs:tests/dir/test.js')
        self.config.add_amd_css(
            'test-css', 'ptah.amdjs:tests/dir/test3.css')

        self.request.matchdict['specname'] = '_'

        resp = amd_init(self.request)
        self.assertIn('var pyramid_amd_modules = {', resp.text)
        self.assertIn(
            '"test-mod": '
            '"/_tests/test.js?_v=4ce2ec81952ee8e6d0058334361babbe"',
            resp.text)
        self.assertIn(
            '"test-css": '
            '"/_tests/test3.css?_v=6305443b362b239fad70ffc6d59c98df"',
            resp.text)

    def test_amd_mod_from_dir(self):
        from ptah.amdjs.amd import amd_init

        self.config.add_amd_dir('ptah.amdjs:tests/dir/')

        self.request.matchdict['specname'] = '_'

        resp = amd_init(self.request)
        self.assertIn(
            '"jca-globals": '
            '"/_tests/test.js?_v=4ce2ec81952ee8e6d0058334361babbe"',
            resp.text)
        self.assertIn(
            '"test3.css": '
            '"/_tests/test3.css?_v=6305443b362b239fad70ffc6d59c98df"',
            resp.text)


class TestInitAmdSpec(PtahTestCase):

    _init_ptah = False

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

    def test_build_md5(self):
        from ptah.amdjs.amd import build_md5, ID_AMD_SPEC, RESOLVER

        f = RESOLVER.resolve('ptah.amdjs:tests/dir/test2.js').abspath()

        reg = self.registry
        reg.settings['amd.enabled'] = True
        reg[ID_AMD_SPEC]['test'] = {'test-init': f}
        reg[ID_AMD_SPEC]['test-init'] = f

        h = build_md5(self.request, 'test')
        self.assertEqual('123', h)

    def test_empty_spec(self):
        self._create_file("[test.js]\nmodules = lib1")

        cfg = self.registry.settings
        cfg['amd.spec'] = ''

        from ptah.amdjs.amd import init_amd_spec, ID_AMD_SPEC

        # no amd-spec-dir
        init_amd_spec(self.config)

        storage = self.registry[ID_AMD_SPEC]
        self.assertEqual(storage, {})

    def test_empty_dir(self):
        fn = self._create_file("[test.js]\nmodules = lib1")

        cfg = self.registry.settings
        cfg['amd.spec'] = ['%s' % fn, 'test:%s' % fn]

        from ptah.amdjs.amd import init_amd_spec

        # no amd-spec-dir
        self.assertRaises(ConfigurationError, init_amd_spec, self.config)

    def test_simple(self):
        fn = self._create_file("[test.js]\nmodules = lib1")

        cfg = self.registry.settings
        cfg['amd.spec'] = [('', '%s' % fn), ('test', fn)]
        cfg['amd.spec-dir'] = 'ptah.amdjs:tests/dir/'

        from ptah.amdjs.amd import init_amd_spec, ID_AMD_SPEC
        init_amd_spec(self.config)

        storage = self.registry[ID_AMD_SPEC]
        self.assertIn('', storage)
        self.assertTrue(storage['']['test.js']['path'].endswith('/test.js'))
        self.assertIn('test', storage)

    text1 = """
[test.js]
modules = lib1

[test.js]
modules = lib2
"""

    def test_multple_bundles(self):
        fn = self._create_file(self.text1)

        cfg = self.registry.settings
        cfg['amd.spec'] = [('test', fn), ('test', fn)]
        cfg['amd.spec-dir'] = '/unknown'

        from ptah.amdjs.amd import init_amd_spec
        self.assertRaises(ConfigurationError, init_amd_spec, self.config)

    def test_register_static_view_for_specs(self):
        from ptah.amdjs.amd import init_amd_spec, RESOLVER

        d = RESOLVER.resolve('ptah.amdjs:tests/dir/').abspath()

        cfg = self.registry.settings
        cfg['amd.spec'] = [('test', 'test2.js')]
        cfg['amd.spec-dir'] = d

        m_asv = self.config.add_static_view = mock.Mock()

        init_amd_spec(self.config)
        self.assertTrue(m_asv.called)

        name, path = m_asv.call_args[0]
        self.assertEqual('_amdjs/bundles/', name)
        self.assertTrue(path.endswith('ptah/amdjs/tests/dir'))


class TestSpecSettings(TestCase):

    _init_ptah = False

    def test_spec_settings(self):
        config = Configurator(settings={'amd.spec-dir': './',
                                        'amd.spec.main': '/test',
                                        'amd.spec.second': '/test1'})

        from ptah.amdjs import includeme

        includeme(config)

        settings = config.get_settings()
        self.assertIn('amd.spec', settings)
        self.assertEqual(
            settings['amd.spec'], [('main', '/test'), ('second', '/test1')])


class TestRequestRenderers(PtahTestCase):

    _init_ptah = False

    def setUp(self):
        super(TestRequestRenderers, self).setUp()

        from ptah.amdjs import amd

        self.cfg = self.registry.settings
        self.registry[amd.ID_AMD_BUILD_MD5] = lambda r, s: '123'

        from pyramid.interfaces import IRequestExtensions
        extensions = self.registry.getUtility(IRequestExtensions)
        self.request._set_extensions(extensions)

    def make_request(self):
        from pyramid.request import Request
        return Request(environ=self._environ)

    def test_render_init_amd(self):
        self.cfg['amd.enabled'] = False

        text = self.request.init_amd().strip()
        self.assertEqual(
            '<script src="http://example.com/_amd__.js?_v=123"> </script>',
            text)

        text = self.request.init_amd('test-spec').strip()
        self.assertIn(
            '<script src="http://example.com/_amd__.js?_v=123"> </script>',
            text)

    def test_include_js(self):
        text = self.request.include_js('test').strip()
        self.assertIn(
            "curl({paths:pyramid_amd_modules},['test'])", text)

        text = self.request.include_js('test', 'test-css').strip()
        self.assertIn(
            "curl({paths:pyramid_amd_modules},['test','css!test-css.css'])",
            text)

    def test_include_css(self):
        text = self.request.include_css('test-css').strip()
        self.assertIn(
            "curl({paths:pyramid_amd_modules},['css!test-css'])", text)

    def test_render_js_includes_unknown_spec(self):
        self.cfg['amd.enabled'] = True

        self.assertRaises(
            RuntimeError, self.request.init_amd, 'unknown')
        self.assertRaises(
            RuntimeError, self.request.init_amd, 'spec')

    def test_render_js_includes_default(self):
        self.cfg['amd.enabled'] = True

        text = self.request.init_amd().strip()
        self.assertEqual(
            '<script src="http://example.com/_amd__.js?_v=123"> </script>',
            text)

    def test_render_amd_includes_spec(self):
        from ptah.amdjs.amd import init_amd_spec, ID_AMD_SPEC, RESOLVER

        self.cfg['amd.enabled'] = True
        self.cfg['amd.spec-dir'] = RESOLVER.resolve(
            'ptah.amdjs:tests/dir/').abspath()
        self.cfg['amd.spec'] = [('test', 'test.js')]
        init_amd_spec(self.config)

        self.registry[ID_AMD_SPEC] = {
            'test': {'test.js': {'path': '/test/test.js'}},
            'test-init': RESOLVER.resolve(
                'ptah.amdjs:tests/dir/test2.js').abspath()}

        text = self.request.init_amd('test').strip()
        self.assertIn(
            '<script src="http://example.com/_amdjs/'
            'bundles/test2.js?_v=123"> </script>', text)

        m_static = self.request.static_url = mock.Mock()
        m_static.return_value = 'http://example.com/_amd_test/test.js'

        text = self.request.init_amd('test', 'test').strip()
        self.assertIn(
            '<script src="http://example.com/_amd_test/test.js"> </script>\n'
            '<script src="http://example.com/_amd_test/test.js"></script>',
            text)


class TestExtractMod(TestCase):

    _init_ptah = False

    def test_extract_mod(self):
        from ptah.amdjs.amd import extract_mod

        res = extract_mod(
            'test', "define('test2', ['test3', 'test4'], function(){})", None)
        self.assertEqual(list(res), [('test2', ['test3', 'test4'])])

    @mock.patch('ptah.amdjs.amd.log')
    def test_extract_mod_empty_name(self, log):
        from ptah.amdjs.amd import extract_mod

        self.assertRaises(
            ConfigurationError,
            extract_mod,
            'test', "define(['test3', 'test4'], function(){})", '/test')
        self.assertEqual("Can't detect amdjs module name for: /test",
                         log.warning.call_args[0][0])

    def test_extract_mod_no_func(self):
        from ptah.amdjs.amd import extract_mod

        self.assertRaises(
            ConfigurationError,
            extract_mod, 'test', "define('test', )", None)
