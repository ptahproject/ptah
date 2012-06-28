import os, shutil
import sys
import tempfile

import ptah
from ptah.scripts import manage
from pyramid.compat import NativeIO

from ptah.scripts import amd


class TestAmdCommand(ptah.PtahTestCase):

    _init_ptah = False

    def test_no_params(self):
        self.init_ptah()

        sys.argv[:] = ['ptah-manage', 'ptah.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        amd.main(False)
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('[-h] [-b] [-m] [--deps] [--no-min] config', val)

    def test_list_modules(self):
        self.init_ptah()

        self.config.register_amd_module(
            'test', 'ptah:tests/dir/test.js', 'Test module')

        sys.argv[1:] = ['-m', 'ptah.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        amd.main(False)
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('* test: ptah:tests/dir/test.js', val)
        self.assertIn('Test module', val)

    def test_build_bundle(self):
        self.init_ptah()
        self.config.register_amd_module(
            'test', 'ptah:tests/dir/test.js', 'Test module')
        self.config.register_mustache_bundle(
            'mustache-test', 'ptah:tests/dir/', 'Mustache bundle')

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH)

        sys.argv[1:] = ['-b', 'ptah.ini']

        stdout = sys.stdout

        out = NativeIO()
        sys.stdout = out
        amd.main(False)
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('Spec files are not specified in .ini file', val)

        cfg['amd-spec'] = ['main:ptah:scripts/tests/amd.spec']

        out = NativeIO()
        sys.stdout = out
        amd.main(False)
        sys.stdout = stdout
        val = out.getvalue()

        self.assertIn('Destination directory is not specified in .ini file',val)

        d = tempfile.mkdtemp()
        cfg['amd-dir'] = d

        out = NativeIO()
        sys.stdout = out
        amd.main(False)
        sys.stdout = stdout
        val = out.getvalue()

        self.assertIn('Processing: main (ptah:scripts/tests/amd.spec)',val)
        self.assertIn("""
* bundle.js
    test: ptah:tests/dir/test.js
    mustache-test: templates bundle""", val)
        self.assertTrue(os.path.isfile(os.path.join(d, 'bundle.js')))
        self.assertFalse(os.path.isfile(os.path.join(d, 'bundle2.js')))

        shutil.rmtree(d)

        d = tempfile.mkdtemp()
        cfg['amd-dir'] = d

        sys.argv[1:] = ['-b', '--no-min', 'ptah.ini']

        out = NativeIO()
        sys.stdout = out
        amd.main(False)
        sys.stdout = stdout
        val = out.getvalue()

        self.assertIn('Processing: main (ptah:scripts/tests/amd.spec)',val)
        self.assertIn("""
* bundle.js
    test: ptah:tests/dir/test.js
    mustache-test: templates bundle""", val)
        self.assertTrue(os.path.isfile(os.path.join(d, 'bundle.js')))

        shutil.rmtree(d)
