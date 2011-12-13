import sys
import unittest
from pyramid.router import Router
from pyramid.config import Configurator

import ptah


class TestPtahInit(unittest.TestCase):

    def test_init_includeme(self):
        config = Configurator()
        config.include('ptah')

        self.assertTrue(hasattr(config, 'ptah_initialize'))

    def test_init_ptah_init(self):
        config = Configurator(
            settings = {'sqla.url': 'sqlite://', 'ptah.excludes': ''})

        data = [False, False]

        def settings_initialized_handler(ev):
            data[1] = True

        sm = config.registry
        sm.registerHandler(
            settings_initialized_handler,
            (ptah.events.SettingsInitialized,))

        config.include('ptah')
        config.ptah_initialize()

        self.assertTrue(data[1])

    def test_init_ptah_init_settings_exception(self):
        config = Configurator(
            settings = {'sqla.url': 'sqlite://'})

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
            config.ptah_initialize()
        except Exception as e:
            err = e

        self.assertIsInstance(err, ptah.config.StopException)
        self.assertIsInstance(err.exc, CustomException)
