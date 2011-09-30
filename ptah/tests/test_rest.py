import unittest
from memphis import config
from pyramid.httpexceptions import HTTPNotFound

from base import Base


class TestRestRegistrations(Base):

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        super(TestRestRegistrations, self).tearDown()

    def test_rest_registerService(self):
        import ptah.rest

        srv = ptah.rest.restService('test', 'Test service')
        self._init_memphis()

        self.assertEqual(srv.name, 'test')
        self.assertIn('test', ptah.rest.services)
        self.assertIn(srv, ptah.rest.services.values())

    def test_rest_registerService_conflicts(self):
        import ptah.rest

        ptah.rest.restService('test', 'Test service')
        ptah.rest.restService('test', 'Test service2')

        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_rest_registerService_action(self):
        import ptah.rest

        srv = ptah.rest.restService('test', 'Test service')

        @srv.action('action', 'Action')
        def raction(request, *args):
            """ doc string """
            return 'test'
        
        self.assertIn('action', srv.actions)

        ac = srv.actions['action']
        self.assertEqual(ac.name, 'action')
        self.assertEqual(ac.title, 'Action')
        self.assertEqual(ac.description, ' doc string ')
        self.assertEqual(ac.callable, raction)
        self.assertEqual(srv(None, 'action'), 'test')
        self.assertRaises(HTTPNotFound, srv, None, 'unknown')

    def test_rest_registerService_apidoc(self):
        import ptah.rest

        ptah.rest.restService('test', 'Test service')
        srv = ptah.rest.services['test']

        @srv.action('action', 'Action')
        def raction(request, *args):
            """ doc string """

        self.assertIn('apidoc', srv.actions)

        info = srv(self._makeRequest(), 'apidoc')

        self.assertEqual(info['name'], 'test')
        self.assertEqual(info['title'], 'Test service')
        self.assertEqual(len(info['actions']), 2)

        self.assertEqual(info['actions'][0]['name'], 'apidoc')
        self.assertEqual(
            info['actions'][0]['link'], 'http://localhost:8080/apidoc')
        self.assertEqual(info['actions'][1]['name'], 'action')
        self.assertEqual(
            info['actions'][1]['link'], 'http://localhost:8080/action')


#class TestRestView(Base):

#    def tearDown(self):
#        config.cleanUp(self.__class__.__module__)
#        super(TestRestApi, self).tearDown()

