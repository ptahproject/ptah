import os, tempfile
import ptah
from pyramid.config import Configurator
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
        self.assertEqual(data['test'], 'ptah:tests/dir/test.js')

    def test_reg_conflict(self):
        self.init_ptah()

        self.config.register_amd_module(
            'test', 'ptah:tests/dir/test1.js')
        self.config.register_amd_module(
            'test', 'ptah:tests/dir/test2.js')

        self.assertRaises(
            ConfigurationConflictError, self.config.commit)


class TestptahInit(ptah.PtahTestCase):

    def setUp(self):
        super(TestptahInit, self).setUp()

        self.config.add_static_view('_tests', 'ptah:tests/dir/')

    def test_amd_mod_paths(self):
        from ptah.amd import amd_init

        self.config.register_amd_module(
            'test-mod', 'ptah:tests/dir/test.js')

        self.request.matchdict['specname'] = '_'

        resp = amd_init(self.request)
        self.assertIn('var ptah_amd_modules = {', resp.body)
        self.assertIn(
            '"test-mod": "http://example.com/_tests/test"', resp.body)


class TestInitAmdSpec(ptah.PtahTestCase):

    def setUp(self):
        self._files = []
        super(TestInitAmdSpec, self).setUp()

    def _create_file(self, text):
        d, fn = tempfile.mkstemp()
        self._files.append(fn)
        with open(fn, 'wb') as f:
            f.write(text)

        return fn

    def tearDown(self):
        for f in self._files:
            os.unlink(f)

        super(TestInitAmdSpec, self).tearDown()

    def test_simple(self):
        fn = self._create_file("[test.js]\nmodules = lib1")

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['amd-specs'] = ['%s'%fn, 'test:%s'%fn]

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
        cfg['amd-specs'] = [fn]

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
        cfg['amd-specs'] = ['test:%s'%fn, 'test:%s'%fn]

        from ptah.amd import init_amd_spec
        self.assertRaises(ConfigurationError, init_amd_spec, self.config)


class TestAmdSpec(ptah.PtahTestCase):

    def test_unknown(self):
        self.request.matchdict['name'] = 'unknown'
        self.request.matchdict['specname'] = 'unknown'

        from ptah.amd import amd_spec
        self.assertIsInstance(amd_spec(self.request), HTTPNotFound)
