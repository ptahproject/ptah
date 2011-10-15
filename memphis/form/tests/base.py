""" base class """
import unittest
from memphis import config
from pyramid import testing
from pyramid.threadlocal import manager
from zope.interface.registry import Components


class Base(unittest.TestCase):

    def _init_memphis(self, settings={}, handler=None, *args, **kw):
        config.initialize(('memphis.view', self.__class__.__module__),
                          reg = Components('test'))
        config.initialize_settings(settings, self.p_config)

    def _setup_pyramid(self):
        self.request = request = testing.DummyRequest()
        request.params = {}
        self.p_config = testing.setUp(request=request)
        self.p_config.get_routes_mapper()

    def _setup_memphis(self):
        config.initialize(('memphis.view', self.__class__.__module__))

    def setUp(self):
        self._setup_pyramid()
        self._setup_memphis()

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        sm = self.p_config
        sm.__init__('base')
        testing.tearDown()
