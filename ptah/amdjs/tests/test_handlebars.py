import mock
import unittest
import os
import tempfile
import shutil
import time
from pyramid.compat import text_type, NativeIO
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationError, ConfigurationConflictError
from pyramid.httpexceptions import HTTPNotFound

from ptah.testing import PtahTestCase


class TestBundleDirective(PtahTestCase):

    _include = False
    _init_ptah = False

    def test_amd_directive(self):
        self.assertFalse(hasattr(self.config, 'add_handlebars_bundle'))
        self.config.include('ptah.amdjs')

        self.assertTrue(hasattr(self.config, 'add_handlebars_bundle'))

    def test_handlebars_mod(self):
        self.config.include('ptah.amdjs')
        self.config.include('ptah.amdjs.static')

        from ptah.amdjs import amd

        text = amd.build_init(self.request, '_')
        self.assertIn(
            '"handlebars": '
            '"/_amdjs_handlebars/static/handlebars.runtime.js?_v=', text)


class TestBundleReg(PtahTestCase):

    _auto_commit = False
    _init_ptah = False

    def test_bundle_registration(self):
        from ptah.amdjs.handlebars import ID_BUNDLE

        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle/',
            i18n_domain='pyramid')
        self.config.commit()

        data = self.registry.get(ID_BUNDLE)
        self.assertIn('test-bundle', data)

        intr = data['test-bundle']
        self.assertTrue(intr['abs_path'].endswith('tests/bundle/'))
        self.assertEqual(intr['i18n_domain'], 'pyramid')

    def test_bundle_unknown(self):
        self.assertRaises(
            ConfigurationError,
            self.config.add_handlebars_bundle,
            'test-bundle', 'ptah.amdjs:tests/unknown/')

    def test_bundle_empty_path(self):
        self.assertRaises(
            ConfigurationError,
            self.config.add_handlebars_bundle, 'test-bundle')

    def test_bundle_not_dir(self):
        self.assertRaises(
            ConfigurationError,
            self.config.add_handlebars_bundle,
            'test-bundle', 'ptah.amdjs:tests/bundle/cat1/form.handlebars')

    def test_bundle_conflict(self):
        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle/')
        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle/')

        self.assertRaises(
            ConfigurationConflictError, self.config.commit)


class TestBundleRoute(PtahTestCase):

    _init_ptah = False
    _settings = {'amd.debug': 'f'}

    def test_unknown_bundle(self):
        from ptah.amdjs.handlebars import bundle_view

        self.request.matchdict['name'] = 'unknown'

        res = bundle_view(self.request)
        self.assertIsInstance(res, HTTPNotFound)

    def test_route(self):
        from ptah.amdjs.handlebars import bundle_view

        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle/')
        self.request.matchdict['name'] = 'test-bundle'

        res = bundle_view(self.request)
        self.assertIn(
            '"test-bundle",["pyramid:templates","handlebars"],', res.text)
        self.assertIn(
            '"cat2":new templates.Bundle("cat2",{"form2"', res.text)

    @mock.patch('ptah.amdjs.handlebars.log')
    def test_route_err_in_template(self, m_log):
        from ptah.amdjs.handlebars import bundle_view

        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle3/')
        self.request.matchdict['name'] = 'test-bundle'

        bundle_view(self.request)
        arg = m_log.error.call_args[0][0]
        self.assertTrue(arg.startswith('Compilation is failed'))
        self.assertTrue(arg.endswith('tests/bundle3/form.hb'))

    def test_list_bundles(self):
        from ptah.amdjs.handlebars import list_bundles

        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle/')

        res = list_bundles(self.request)
        self.assertEqual('test-bundle', res[0][0])
        self.assertTrue(res[0][1].startswith(
            'http://example.com/_handlebars/test-bundle.js?_v'))

    def test_list_bundles_unset(self):
        from ptah.amdjs.handlebars import list_bundles

        config = Configurator()
        request = self.make_request()
        request.registry = config.registry

        self.assertEqual(list_bundles(request), [])

    def test_bundles_amd(self):
        from ptah.amdjs.amd import amd_init

        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle/')

        self.request.matchdict['specname'] = '_'

        res = amd_init(self.request)
        self.assertIn(
            '"test-bundle":"/_handlebars/test-bundle.js?_v=', res.text)

    def test_bundles_amd_spec(self):
        from ptah.amdjs.amd import amd_init, ID_AMD_SPEC

        self.registry[ID_AMD_SPEC] = {
            'test': {'test-bundle':
                     {'name': 'bundle',
                      'md5': '123',
                      'path': 'ptah.amdjs:static/example.js'}}
        }
        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle/')

        self.request.matchdict['specname'] = 'test'

        res = amd_init(self.request)
        self.assertIn(
            '"test-bundle":"/_amdjs/static/example.js?_v=123"', res.text)

    def test_build_bundle(self):
        from ptah.amdjs.handlebars import bundle_view

        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle/')
        self.request.matchdict['name'] = 'test-bundle'

        res = bundle_view(self.request)
        self.assertIn(
            '"form-window":Handlebars.template(function', res.text)

    @mock.patch('ptah.amdjs.handlebars.compat')
    def test_build_bundle_no_node(self, m_comp):
        from ptah.amdjs.handlebars import bundle_view

        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle/')
        self.request.matchdict['name'] = 'test-bundle'

        m_comp.NODE_PATH = None

        res = bundle_view(self.request)
        self.assertIn(
            'form-window":Handlebars.compile("<div class=', res.text)

    @mock.patch('ptah.amdjs.handlebars.get_localizer')
    def test_build_bundle_toplevel_i18n(self, m_loc):
        from ptah.amdjs.handlebars import bundle_view

        cfg = self.registry.settings
        cfg['amd.tmpl-langs'] = ['en', 'pt_BR']

        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle2/',
            i18n_domain='pyramid')
        self.request.matchdict['name'] = 'test-bundle'

        class loc(object):
            def translate(self, t, i18n):
                if m_loc.call_args[0][0].locale_name == 'pt_BR':
                    return 'Senha'
                return t

        m_loc.return_value = loc()

        res = bundle_view(self.request)
        self.assertIn(
            "Handlebars.registerHelper('i18n-test-bundle'", res.text)
        self.assertIn(
            'var bundle=new templates.Bundle("test-bundle",{"form"', res.text)
        self.assertIn(
            'bundle.__i18n__ = {"Password": {"pt_BR": "Senha"}}', res.text)

    @mock.patch('ptah.amdjs.handlebars.compat')
    @mock.patch('ptah.amdjs.handlebars.get_localizer')
    def test_build_bundle_toplevel_i18n_no_nodejs(self, m_loc, m_com):
        from ptah.amdjs.handlebars import bundle_view

        cfg = self.registry.settings
        cfg['amd.tmpl-langs'] = ['en', 'pt_BR']

        self.config.add_handlebars_bundle(
            'test-bundle', 'ptah.amdjs:tests/bundle2/',
            i18n_domain='pyramid')
        self.request.matchdict['name'] = 'test-bundle'

        class loc(object):
            def translate(self, t, i18n):
                if m_loc.call_args[0][0].locale_name == 'pt_BR':
                    return 'Senha'
                return t

        m_loc.return_value = loc()
        m_com.NODE_PATH = None

        res = bundle_view(self.request)
        self.assertIn(
            "Handlebars.registerHelper('i18n-test-bundle'", res.text)
        self.assertIn(
            'var bundle=new templates.Bundle("test-bundle",'
            '{"form":Handlebars.compile(', res.text)
        self.assertIn(
            'bundle.__i18n__ = {"Password": {"pt_BR": "Senha"}}', res.text)


class TestBuildBundle(PtahTestCase):

    _init_ptah = False

    def setUp(self):
        super(TestBuildBundle, self).setUp()

        self.path = tempfile.mkdtemp()
        self.cfg = self.registry.settings

        from ptah.amdjs import handlebars
        self.storage = self.registry.get(handlebars.ID_BUNDLE)

        self.addCleanup(shutil.rmtree, self.path)

    def test_compile_new(self):
        from ptah.amdjs import handlebars

        self.cfg['amd.tmpl-cache'] = self.path
        prefix = os.path.split(self.path)[-1]

        f = os.path.join(self.path, 'template')
        with open(f, 'w') as fn:
            fn.write('<div>{{test}}</div>')

        tmpl = text_type(handlebars.compile_template(
            'test', f, handlebars.compat.NODE_PATH, self.path)[0])

        self.assertTrue(os.path.isfile(
            os.path.join(self.path, 'test-%s-template' % prefix)))
        self.assertTrue(os.path.isfile(
            os.path.join(
                self.path,
                'test-%s-template.js.%s' % (prefix, handlebars.VERSION))))

        self.assertIn(
            'function (Handlebars,depth0,helpers,partials,data) {', tmpl)

    def test_compile_no_node(self):
        from ptah.amdjs import handlebars

        self.cfg['amd.tmpl-cache'] = self.path
        prefix = os.path.split(self.path)[-1]

        f = os.path.join(self.path, 'template')
        with open(f, 'w') as fn:
            fn.write('<div>{{test}}</div>')

        tmpl = text_type(handlebars.compile_template(
            'test', f, None, self.path)[0])

        self.assertTrue(os.path.isfile(
            os.path.join(self.path, 'test-%s-template' % prefix)))
        self.assertTrue(os.path.isfile(
            os.path.join(self.path, 'test-%s-template.pre' % prefix)))
        self.assertIn('<div>{{test}}</div>', tmpl)

    def test_compile_new_i18n(self):
        from ptah.amdjs import handlebars

        self.cfg['amd.tmpl-cache'] = self.path
        prefix = os.path.split(self.path)[-1]

        f = os.path.join(self.path, 'template')
        with open(f, 'w') as fn:
            fn.write('<div>{{test}}{{#i18n}}i18n text{{/i18n}}</div>')

        tmpl, i18n = handlebars.compile_template(
            'test', f, handlebars.compat.NODE_PATH, self.path)
        tmpl = text_type(tmpl)

        self.assertIn('i18n text', i18n)
        self.assertTrue(os.path.isfile(
            os.path.join(self.path, 'test-%s-template.i18n' % prefix)))
        self.assertEqual(
            open(os.path.join(
                self.path, 'test-%s-template' % prefix), 'r').read(),
            '<div>{{test}}{{#i18n-test}}i18n text{{/i18n-test}}</div>')

    def test_compile_existing(self):
        from ptah.amdjs import handlebars

        self.cfg['amd.tmpl-cache'] = self.path
        prefix = os.path.split(self.path)[-1]

        f = os.path.join(self.path, 'template')
        with open(f, 'w') as fn:
            fn.write('<div>{{test}}</div>')

        time.sleep(0.01)

        f1 = os.path.join(self.path, 'test-%s-template' % prefix)
        with open(f1, 'w') as fn:
            fn.write('existing1')

        time.sleep(0.01)

        f2 = os.path.join(
            self.path, 'test-%s-template.js.%s' % (prefix, handlebars.VERSION))
        with open(f2, 'w') as fn:
            fn.write('existing2')

        tmpl = text_type(handlebars.compile_template(
            'test', f, handlebars.compat.NODE_PATH, self.path)[0])

        self.assertEqual('existing2', tmpl)

    def test_compile_existing_i18n(self):
        """
        Skip compilation if it is compiled already
        """
        from ptah.amdjs import handlebars

        self.cfg['amd.tmpl-cache'] = self.path
        prefix = os.path.split(self.path)[-1]

        f = os.path.join(self.path, 'template')
        with open(f, 'w') as fn:
            fn.write('<div>{{test}}</div>')

        time.sleep(0.01)

        f1 = os.path.join(self.path, 'test-%s-template' % prefix)
        with open(f1, 'w') as fn:
            fn.write('existing1')

        time.sleep(0.01)

        f2 = os.path.join(
            self.path, 'test-%s-template.js.%s' % (prefix, handlebars.VERSION))

        with open(f2, 'w') as fn:
            fn.write('existing2')

        time.sleep(0.01)

        f1 = os.path.join(self.path, 'test-%s-template.i18n' % prefix)
        with open(f1, 'w') as fn:
            fn.write('["existing3"]')

        tmpl, i18n = handlebars.compile_template(
            'test', f, handlebars.compat.NODE_PATH, self.path)

        self.assertEqual(['existing3'], i18n)


class TestExtractI18N(unittest.TestCase):

    _init_ptah = False

    def test_extract(self):
        from ptah.amdjs.handlebars import extract_i18n

        f = NativeIO('<div>{{#i18n}}Test \n message{{/i18n}}</div>')

        d = extract_i18n(f, [], [], [])
        self.assertEqual(d[0], (5, None, text_type('Test \n message'), []))


class TestNoNodeJS(PtahTestCase):

    _init_ptah = False

    def setUp(self):
        from ptah.amdjs import handlebarsjs
        self.node_path = handlebarsjs.NODE_PATH

        handlebarsjs.NODE_PATH = None

        super(TestNoNodeJS, self).setUp()

    def tearDown(self):
        from ptah.amdjs import handlebarsjs
        handlebarsjs.NODE_PATH = self.node_path

    def test_handlebars_mod(self):
        from ptah.amdjs import amd

        text = amd.build_init(self.request, '_')
        self.assertIn(
            '"handlebars": "/_amdjs_handlebars/static/handlebars.js?_v=', text)
