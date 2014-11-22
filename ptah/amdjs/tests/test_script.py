import mock
import os
import shutil
import sys
import tempfile
from pyramid.compat import NativeIO
from ptah.amdjs import script as amd
from ptah.amdjs.amd import ID_AMD_MODULE, ID_AMD_SPEC

from ptah.testing import PtahTestCase


class TestAmdCommand(PtahTestCase):

    _init_ptah = False

    @mock.patch('ptah.amdjs.script.bootstrap')
    def test_no_params(self, m_bs):
        m_bs.return_value = {
            'registry': self.registry, 'request': self.request}

        sys.argv[:] = ['amdjs', 'ptah.amdjs.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        amd.main()
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('[-h] [-b] [-m] [--deps] [--no-min] config', val)

    @mock.patch('ptah.amdjs.script.bootstrap')
    def test_list_modules(self, m_bs):
        m_bs.return_value = {
            'registry': self.registry, 'request': self.request}

        self.config.add_amd_js(
            'test', 'ptah.amdjs:tests/dir/test.js', 'Test module')

        sys.argv[1:] = ['-m', 'ptah.amdjs.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        amd.main()
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('* test: ptah.amdjs:tests/dir/test.js', val)
        self.assertIn('Test module', val)

    @mock.patch('ptah.amdjs.script.build_init')
    @mock.patch('ptah.amdjs.script.bootstrap')
    def test_build_bundle(self, m_bs, m_binit):
        m_bs.return_value = {'registry': self.registry,
                             'request': self.request}
        m_binit.return_value = '123'

        self.config.add_amd_js(
            'test', 'ptah.amdjs:tests/dir/test.js', 'Test module')
        self.config.add_handlebars_bundle(
            'handlebars-test', 'ptah.amdjs:tests/dir/', 'Handlebars bundle')

        cfg = self.registry.settings

        sys.argv[1:] = ['-b', 'ptah.amdjs.ini']

        stdout = sys.stdout

        out = NativeIO()
        sys.stdout = out
        amd.main()
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('Spec files are not specified in .ini file', val)

        cfg['amd.spec'] = [('main', 'ptah.amdjs:tests/amd.spec')]

        out = NativeIO()
        sys.stdout = out
        amd.main()
        sys.stdout = stdout
        val = out.getvalue()

        self.assertIn(
            'Destination directory is not specified in .ini file', val)

        d = tempfile.mkdtemp()
        cfg['amd.spec-dir'] = d

        out = NativeIO()
        sys.stdout = out
        amd.main()
        sys.stdout = stdout
        val = out.getvalue()

        self.assertIn('Processing: main (ptah.amdjs:tests/amd.spec)', val)
        self.assertIn("""
* bundle.js
    test: ptah.amdjs:tests/dir/test.js
    handlebars-test: templates bundle""", val)
        self.assertTrue(os.path.isfile(os.path.join(d, 'bundle.js')))
        self.assertFalse(os.path.isfile(os.path.join(d, 'bundle2.js')))
        self.assertTrue(os.path.isfile(os.path.join(d, 'init-main.js')))

        shutil.rmtree(d)

        d = tempfile.mkdtemp()
        cfg['amd.spec-dir'] = d

        sys.argv[1:] = ['-b', '--no-min', 'ptah.amdjs.ini']

        out = NativeIO()
        sys.stdout = out
        amd.main()
        sys.stdout = stdout
        val = out.getvalue()

        self.assertIn('Processing: main (ptah.amdjs:tests/amd.spec)', val)
        self.assertIn("""
* bundle.js
    test: ptah.amdjs:tests/dir/test.js
    handlebars-test: templates bundle""", val)
        self.assertTrue(os.path.isfile(os.path.join(d, 'bundle.js')))

        shutil.rmtree(d)

    @mock.patch('ptah.amdjs.script.bootstrap')
    def test_extract_deps(self, m_bs):
        m_bs.return_value = {'registry': self.registry,
                             'request': self.request}
        sys.argv[1:] = ['-b', '--no-min', 'ptah.amdjs.ini']

        args = amd.AmdjsCommand.parser.parse_args()
        cmd = amd.AmdjsCommand(args)

        self.assertEqual(
            ['jca'],
            cmd.extract_deps({'path': 'ptah.amdjs:tests/dir/test.js'}))

        self.assertEqual(
            ['jca'],
            cmd.extract_deps({'path': '', 'requires': ['jca']}))

    @mock.patch('ptah.amdjs.script.bootstrap')
    def test_build_tree(self, m_bs):
        m_bs.return_value = {'registry': self.registry,
                             'request': self.request}
        sys.argv[1:] = ['--deps', 'ptah.amdjs.ini']

        self.registry[ID_AMD_MODULE] = {
            'test': {'path': 'ptah.amdjs:tests/dir/test.js'}}

        self.registry[ID_AMD_SPEC] = {'test': {'test': {}}}

        out = NativeIO()
        stdout = sys.stdout
        sys.stdout = out
        amd.main()
        sys.stdout = stdout
        val = out.getvalue()

        self.assertIn('* Spec: test', val)
        self.assertIn('jca', val)
        self.assertIn('test', val)
