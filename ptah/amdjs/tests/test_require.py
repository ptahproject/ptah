""" Tests for ptah.amdjs.require module """
import mock
from pyramid.compat import text_

from ptah.testing import PtahTestCase
from ptah.amdjs.amd import RESOLVER, ID_AMD_SPEC, init_amd_spec


class TestRequire(PtahTestCase):

    _init_ptah = False

    def setUp(self):
        super(TestRequire, self).setUp()

        self.data = self.request.amdjs_data = {
            'js': [], 'css': [], 'spec': '', 'fn': [], 'init': False}

    def test_require(self):
        self.request.require('mod1')
        self.assertTrue(self.data['init'])
        self.assertEqual(['mod1'], self.data['js'])

    def test_require_unique(self):
        self.request.require('mod1', 'mod2', 'mod1')
        self.assertEqual(['mod1', 'mod2'], self.data['js'])

        self.request.require('mod1', 'mod2', 'mod1')
        self.assertEqual(['mod1', 'mod2'], self.data['js'])

    def test_require_js(self):
        self.request.require_js('mod1')
        self.assertTrue(self.data['init'])
        self.assertEqual(['mod1'], self.data['js'])

    def test_require_js_unique(self):
        self.request.require_js('mod1', 'mod2', 'mod1')
        self.assertEqual(['mod1', 'mod2'], self.data['js'])

        self.request.require_js('mod1', 'mod2', 'mod1')
        self.assertEqual(['mod1', 'mod2'], self.data['js'])

    def test_require_css(self):
        self.request.require_css('mod1')
        self.assertTrue(self.data['init'])
        self.assertEqual(['mod1'], self.data['css'])

    def test_require_css_unique(self):
        self.request.require_css('mod1', 'mod2', 'mod1')
        self.assertEqual(['mod1', 'mod2'], self.data['css'])

        self.request.require_css('mod1', 'mod2', 'mod1')
        self.assertEqual(['mod1', 'mod2'], self.data['css'])

    def test_require_fn(self):
        self.request.require_fn(['jquery'], 'function($){}')
        self.assertTrue(self.data['init'])
        self.assertEqual(["curl(['jquery'], function($){})"], self.data['fn'])

    def test_require_spec(self):
        self.request.require_spec('spec')
        self.assertTrue(self.data['init'])
        self.assertEqual('spec', self.data['spec'])

    @mock.patch('ptah.amdjs.require.log')
    def test_require_spec_mutple_times(self, m_log):
        self.request.require_spec('spec')

        self.request.require_spec('spec2')

        self.assertTrue(m_log.warn.called)
        self.assertEqual('spec', self.data['spec'])


class TestAmdjsTween(PtahTestCase):

    _init_ptah = False

    def setUp(self):
        super(TestAmdjsTween, self).setUp()

        self.request.accept = 'text/html'
        self.request.is_xhr = False

        self.js = []
        self.css = []
        self.fn = []
        self.spec = '_'

        self.response = self.request.response
        self.response.status_code = 200
        self.response.content_type = 'text/html; charset=utf-8'
        self.response.text = text_('<html><body><h1>Test</h1></body></html>')

    def _handler(self, request):
        if self.js:
            self.request.require_js(*self.js)
        if self.css:
            self.request.require_js(*self.js)
        for r, fn in self.fn:
            self.request.require_fn(r, fn)

        if self.spec:
            self.request.require_spec(self.spec)

        return self.response

    def _make_one(self, request):
        from ptah.amdjs.require import amdjs_tween_factory
        return amdjs_tween_factory(self._handler, self.registry)(request)

    def test_non_200_status(self):
        self.response.status_code = 304

        res = self._make_one(self.request)
        self.assertFalse(hasattr(res, '_amdjs_inititalized'))

    def test_accept(self):
        self.request.accept = 'application/json'

        res = self._make_one(self.request)
        self.assertFalse(hasattr(res, '_amdjs_inititalized'))

    def test_xhr(self):
        self.request.is_xhr = True

        res = self._make_one(self.request)
        self.assertFalse(hasattr(res, '_amdjs_inititalized'))

    def test_response_length(self):
        self.response.content_length = 0

        res = self._make_one(self.request)
        self.assertFalse(hasattr(res, '_amdjs_inititalized'))

    def test_tween(self):
        self.js = ['mod1', 'mod2']
        self.css = ['css1']
        self.fn = [(('jquery',), 'function($){}')]
        self.spec = '_'

        res = self._make_one(self.request).text

        self.assertIn(
            '<script src="http://example.com/_amd__.js', res)
        self.assertIn(
            '<script type="text/javascript">curl({paths:pyramid_amd_modules},'
            "['mod1','mod2'])</script>", res)
        self.assertIn(
            "curl(['jquery'], function($){})", res)

    @mock.patch('ptah.amdjs.require.log')
    def test_tween_no_spec(self, m_log):
        self.registry.settings['amd.enabled'] = True
        self.spec = 'test'

        self._make_one(self.request)
        self.assertTrue(m_log.warn.called)

    def test_tween_spec(self):
        self.registry.settings['amd.enabled'] = True
        self.registry.settings['amd.spec-dir'] = RESOLVER.resolve(
            'ptah.amdjs:tests/dir/').abspath()
        self.registry.settings['amd.spec'] = [('test', 'test.js')]
        init_amd_spec(self.config)

        self.registry[ID_AMD_SPEC] = {
            'test': {'test.js': {'path': '/test/test.js'}},
            'test-init': RESOLVER.resolve(
                'ptah.amdjs:tests/dir/test2.js').abspath()}

        self.js = ['mod1', 'mod2']
        self.css = ['css1']
        self.fn = [(('jquery',), 'function($){}')]
        self.spec = 'test'

        res = self._make_one(self.request).text

        self.assertIn(
            '<script src="http://example.com/_amdjs/bundles/test2.js', res)
        self.assertIn(
            '<script type="text/javascript">curl({paths:pyramid_amd_modules},'
            "['mod1','mod2'])</script>", res)
        self.assertIn(
            "curl(['jquery'], function($){})", res)
