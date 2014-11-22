""" Tests for ptah.amdjs.amddebug """
import mock
from ptah.amdjs import amd, amddebug

from ptah.testing import PtahTestCase


class TestAmdDirective(PtahTestCase):

    _settings = {'amd.debug': True}
    _include = False
    _init_ptah = False

    def test_amd_directive(self):
        self.config.include('ptah.amdjs')

        self.assertEqual(
            'ptah.amdjs.amddebug',
            self.config.add_amd_dir.__func__.__module__)

        self.assertEqual(
            'ptah.amdjs.amddebug',
            self.registry[amd.ID_AMD_BUILD].__module__)

        self.assertEqual(
            'ptah.amdjs.amddebug',
            self.registry[amd.ID_AMD_BUILD_MD5].__module__)

    def test_add_amd_dir(self):
        self.config.include('ptah.amdjs')

        self.config.add_amd_dir('ptah.amdjs:tests/dir/')

        path = amd.RESOLVER.resolve('ptah.amdjs:tests/dir/').abspath()

        self.assertEqual(
            [('ptah.amdjs:tests/dir/', path)],
            self.registry.settings['amd.debug.data']['paths'])


class TestBuildInit(PtahTestCase):

    _settings = {'amd.debug': True}
    _init_ptah = False

    @mock.patch('ptah.amdjs.amddebug.build_init')
    def test_build_md5(self, m_binit):
        m_binit.return_value = '123'

        self.assertEqual(
            '202cb962ac59075b964b07152d234b70',
            amddebug.build_md5(self.request, '_'))

    @mock.patch('ptah.amdjs.amddebug.amd')
    def test_build_init(self, m_amd):
        m_amd.build_init.return_value = '123'
        m_amd.extract_mod = amd.extract_mod

        self.config.add_static_view('_tests', 'ptah.amdjs:tests/dir/')
        self.config.add_amd_dir('ptah.amdjs:tests/dir/')

        res = amddebug.build_init(self.request, 'test')
        self.assertEqual('123', res)
        self.assertTrue(m_amd.build_init.called)

        mods = m_amd.build_init.call_args[0][2]
        self.assertIn(
            '"test3.css": '
            '"/_tests/test3.css?_v=6305443b362b239fad70ffc6d59c98df"',
            mods)

        self.assertIn(
            '"jca-globals": '
            '"/_tests/test.js?_v=4ce2ec81952ee8e6d0058334361babbe"',
            mods)
