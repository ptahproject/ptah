import sys
import unittest
from pyramid.router import Router
from pyramid.config import Configurator

import ptah


class TestInitializeSql(unittest.TestCase):

    def test_ptahinit_sqla(self):
        config = Configurator(
            settings = {'sqlalchemy.url': 'sqlite://'})
        config.include('ptah')
        config.commit()

        config.ptah_initialize_sql()
        self.assertIsNotNone(ptah.get_base().metadata.bind)


class TestPtahInit(unittest.TestCase):

    def test_init_includeme(self):
        config = Configurator()
        config.include('ptah')
        config.commit()

        self.assertTrue(hasattr(config, 'ptah_initialize_settings'))
        self.assertTrue(hasattr(config, 'ptah_initialize_sql'))

        from pyramid.interfaces import \
             IAuthenticationPolicy, IAuthorizationPolicy

        self.assertIsNotNone(
            config.registry.queryUtility(IAuthenticationPolicy))
        self.assertIsNotNone(
            config.registry.queryUtility(IAuthorizationPolicy))

    def test_init_ptah_init(self):
        config = Configurator()
            #settings = {'sqlalchemy.url': 'sqlite://'})

        data = [False, False]

        def settings_initialized_handler(ev):
            data[1] = True

        sm = config.registry
        sm.registerHandler(
            settings_initialized_handler,
            (ptah.events.SettingsInitialized,))

        config.include('ptah')
        config.commit()

        config.ptah_initialize_settings()

        self.assertTrue(data[1])

    def test_init_ptah_init_settings_exception(self):
        config = Configurator(
            settings = {'sqlalchemy.url': 'sqlite://'})

        class CustomException(Exception):
            pass

        def initialized_handler(ev):
            raise CustomException()

        sm = config.registry
        sm.registerHandler(
            initialized_handler,
            (ptah.events.SettingsInitialized,))

        config.include('ptah')
        config.commit()

        err = None
        try:
            config.ptah_initialize_settings()
        except Exception as e:
            err = e

        self.assertIsInstance(err, ptah.config.StopException)
        self.assertIsInstance(err.exc, CustomException)
