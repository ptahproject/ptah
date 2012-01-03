import sys
from pyramid.router import Router
from pyramid.config import Configurator

import ptah
from ptah.testing import TestCase


class TestInitializeSql(TestCase):

    def test_ptahinit_sqla(self):
        config = Configurator(
            settings = {'sqlalchemy.url': 'sqlite://'})
        config.include('ptah')
        config.commit()

        config.ptah_init_sql()
        self.assertIsNotNone(ptah.get_base().metadata.bind)


class TestPtahInit(TestCase):

    def test_init_includeme(self):
        config = Configurator()
        config.include('ptah')
        config.commit()

        for name in ('ptah_init_settings', 'ptah_init_sql',
                     'ptah_init_manage', 'ptah_init_mailer',
                     'ptah_init_rest', 'get_cfg_storage',
                     'ptah_get_settings', 'ptah_auth_checker',
                     'ptah_auth_provider', 'ptah_principal_searcher',
                     'ptah_uri_resolver', 'ptah_password_changer',
                     'ptah_layout', 'ptah_snippet',
                     'ptah_populate', 'ptah_populate_step'):
            self.assertTrue(hasattr(config, name))

        from pyramid.interfaces import \
             IAuthenticationPolicy, IAuthorizationPolicy

        self.assertIsNotNone(
            config.registry.queryUtility(IAuthenticationPolicy))
        self.assertIsNotNone(
            config.registry.queryUtility(IAuthorizationPolicy))

    def test_init_ptah_init(self):
        config = Configurator()

        data = [False, False]

        def settings_initialized_handler(ev):
            data[1] = True

        sm = config.registry
        sm.registerHandler(
            settings_initialized_handler,
            (ptah.events.SettingsInitialized,))

        config.include('ptah')
        config.ptah_init_settings()
        config.commit()

        self.assertTrue(data[1])

    def test_init_ptah_init_settings_exception(self):
        config = Configurator(autocommit = True)

        class CustomException(Exception):
            pass

        def initialized_handler(ev):
            raise CustomException()

        sm = config.registry
        sm.registerHandler(
            initialized_handler,
            (ptah.events.SettingsInitialized,))

        config.include('ptah')

        err = None
        try:
            config.ptah_init_settings()
        except Exception as e:
            err = e

        self.assertIsInstance(err, ptah.config.StopException)
        self.assertIsInstance(err.exc, CustomException)


class TestDummyMailer(ptah.PtahTestCase):

    def test_dummy_mailer(self):
        from ptah.ptahsettings import DummyMailer

        PTAH = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)

        self.assertIsInstance(PTAH['Mailer'], DummyMailer)

        PTAH['Mailer'].send('test@example.com', 'to@example.com', 'msg')
