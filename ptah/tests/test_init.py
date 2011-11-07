import sys
import unittest
from pyramid.router import Router
from pyramid.config import Configurator

import ptah


class TestPtahInit(unittest.TestCase):

    def test_init_includeme(self):
        config = Configurator()
        config.include('ptah')

        self.assertTrue(hasattr(config, 'ptah_init'))

    def test_init_ptah_init(self):
        config = Configurator(
            settings = {'sqla.url': 'sqlite://', 'ptah.excludes': ''})

        data = [False, False]

        def initialized_handler(ev):
            data[0] = True

        def settings_initialized_handler(ev):
            data[1] = True

        sm = config.registry
        sm.registerHandler(
            initialized_handler,
            (ptah.config.Initialized,))
        sm.registerHandler(
            settings_initialized_handler,
            (ptah.config.SettingsInitialized,))

        config.include('ptah')
        config.ptah_init()

        self.assertTrue(data[0])
        self.assertTrue(data[1])

    def test_init_ptah_init_exception(self):
        config = Configurator(
            settings = {'sqla.url': 'sqlite://'})

        class CustomException(Exception):
            pass

        def initialized_handler(ev):
            raise CustomException()

        sm = config.registry
        sm.registerHandler(
            initialized_handler,
            (ptah.config.Initialized,))

        config.include('ptah')

        try:
            config.ptah_init()
        except Exception, err:
            pass

        self.assertIsInstance(err, ptah.config.StopException)
        self.assertIsInstance(err.exc, CustomException)

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
            (ptah.config.SettingsInitialized,))

        config.include('ptah')

        try:
            config.ptah_init()
        except Exception, err:
            pass

        self.assertIsInstance(err, ptah.config.StopException)
        self.assertIsInstance(err.exc, CustomException)

    def test_init_wsgi_app(self):
        app = ptah.make_wsgi_app({'sqla.url': 'sqlite://', 'ptah.excludes': ''})
        self.assertIsInstance(app, Router)

    def test_init_wsgi_app_exception(self):
        orig_exit = sys.exit
        orig_ptah_init = ptah.ptah_init

        data = [False]
        def exit(status):
            data[0] = True

        def ptah_init(config):
            raise ptah.config.StopException('')

        sys.exit = exit
        ptah.ptah_init = ptah_init

        app = ptah.make_wsgi_app({})

        sys.exit = orig_exit
        ptah.ptah_init = orig_ptah_init

        self.assertIsNone(app)
        self.assertTrue(data[0])
