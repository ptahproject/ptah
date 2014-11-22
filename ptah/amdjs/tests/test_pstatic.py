""" Tests for {ptah.amdjs.pstatic} """
import mock
from ptah.amdjs import pstatic

from ptah.testing import PtahTestCase


class TestSettingsRewrite(PtahTestCase):

    _settings = {'static.rewrite': 't',
                 'static.url': ''}
    _init_ptah = False

    def test_rewrite_false(self):
        """ If static.url is not set static.rewite always false """
        self.assertFalse(self.config.get_settings()['static.rewrite'])


class TestSettingsRewriteTrue(PtahTestCase):

    _settings = {'static.rewrite': 't',
                 'static.url': 'http://static.example.com'}
    _init_ptah = False

    def test_rewrite(self):
        """ If static.url is not set static.rewite always false """
        self.assertTrue(self.config.get_settings()['static.rewrite'])
        self.assertEqual(
            'http://static.example.com/',
            self.config.get_settings()['static.url'])


class TestStatic(PtahTestCase):

    _init_ptah = False

    def test_register_static_rewrite_enabled(self):
        """ Register static view, static.rewrite is enabled """
        cfg = self.config.get_settings()
        cfg['static.rewrite'] = True
        cfg['static.url'] = 'http://static.example.com/static/'

        self.config.add_static_view(
            'amdjs/static', 'ptah.amdjs:static/')

        self.assertIn(pstatic.ID_STATIC, self.registry)

        data = self.registry[pstatic.ID_STATIC]
        self.assertIn('amdjs/static', data)

    @mock.patch('ptah.amdjs.pstatic.os')
    @mock.patch('ptah.amdjs.pstatic.shutil')
    def test_static_command(self, m_shutil, m_os):
        m_os.path.exists.return_value = True

        cmd = pstatic.StaticCommand('/tmp', self.registry)
        cmd.run()

        self.assertTrue(m_os.path.exists.called)
        self.assertTrue(m_shutil.rmtree.called)
        self.assertTrue(m_shutil.copytree.called)

    @mock.patch('ptah.amdjs.pstatic.bootstrap')
    @mock.patch('ptah.amdjs.pstatic.StaticCommand')
    def test_static_command_main(self, m_cmd, m_bootstrap):
        m_bootstrap.return_value = {'registry': self.registry}
        cmd = m_cmd.return_value = mock.Mock()
        pstatic.main()
        self.assertTrue(cmd.run.called)
