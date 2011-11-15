""" base class """
import unittest
from ptah import config
from pyramid import testing


class Base(unittest.TestCase):

    def _init_ptah(self, settings={}, handler=None, *args, **kw):
        config.initialize(self.p_config, ('ptah', self.__class__.__module__),
                          initsettings=False)
        config.initialize_settings(settings, self.p_config)

    def _setup_pyramid(self):
        self.request = request = testing.DummyRequest()
        request.params = {}
        self.p_config = testing.setUp(request=request)
        self.p_config.get_routes_mapper()
        self.registry = self.p_config.registry
        self.request.registry = self.p_config.registry

    def _setup_ptah(self):
        config.initialize(
            self.p_config, ('ptah.view', self.__class__.__module__),
            initsettings=False)

    def setUp(self):
        self._setup_pyramid()
        self._setup_ptah()

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        sm = self.p_config
        sm.__init__('base')
        testing.tearDown()
