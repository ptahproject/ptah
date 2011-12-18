import ptah
import json
from ptah import config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.exceptions import ConfigurationConflictError

from ptah.testing import PtahTestCase


class TestRestRegistrations(PtahTestCase):

    _init_ptah = False

    def test_rest_registerService(self):
        import ptah.rest

        srv = ptah.rest.RestService('test', 'Test service')
        self.init_ptah()

        services = config.get_cfg_storage(ptah.rest.ID_REST)

        self.assertEqual(srv.name, 'test')
        self.assertIn('test', services)
        self.assertIn(srv, services.values())

    def test_rest_registerService_conflicts(self):
        import ptah.rest

        ptah.rest.RestService('test', 'Test service')
        ptah.rest.RestService('test', 'Test service2')

        self.assertRaises(ConfigurationConflictError, self.init_ptah)

    def test_rest_registerService_action(self):
        import ptah.rest

        srv = ptah.rest.RestService('test', 'Test service')

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

        ptah.rest.RestService('test', 'Test service')
        self.init_ptah()

        srv = config.get_cfg_storage(ptah.rest.ID_REST)['test']

        @srv.action('action', 'Action')
        def raction(request, *args):
            """ doc string """

        self.assertIn('apidoc', srv.actions)

        info = srv(self.make_request(), 'apidoc')

        self.assertEqual(info['name'], 'test')
        self.assertEqual(info['title'], 'Test service')
        self.assertEqual(len(info['actions']), 2)

        self.assertEqual(info['actions'][0]['name'], 'apidoc')
        self.assertEqual(
            info['actions'][0]['__link__'], 'http://example.com/apidoc')
        self.assertEqual(info['actions'][1]['name'], 'action')
        self.assertEqual(
            info['actions'][1]['__link__'], 'http://example.com/action')


class Principal(object):
    __uri__ = 'testprincipal:1'
    name = 'admin'
    login = 'admin'


class Provider(object):
    principal = Principal()

    def authenticate(self, creds):
        return self.principal


class TestRestView(PtahTestCase):

    _init_ptah = False
    _init_sqla = False
    _settings = {'auth.secret': 'test'}

    def test_rest_enable_api(self):
        from ptah.rest import RestLoginRoute, RestApiRoute

        mapper = self.config.get_routes_mapper()

        self.assertIsNone(mapper.get_route('ptah-rest'))
        self.assertIsNone(mapper.get_route('ptah-rest-login'))
        self.init_ptah()

        self.config.ptah_init_rest()

        marker = object()

        factory = mapper.get_route('ptah-rest').factory
        self.assertIs(factory, RestApiRoute)
        self.assertIs(factory(marker).request, marker)

        factory = mapper.get_route('ptah-rest-login').factory
        self.assertIs(factory, RestLoginRoute)
        self.assertIs(factory(marker).request, marker)

    def test_rest_login(self):
        from ptah.rest import Login

        request = DummyRequest()
        login = Login(request)

        self.assertIn('authentication failed', login().text)
        self.assertEqual(request.response.status, '403 Forbidden')

    def test_rest_login_success(self):
        from ptah.rest import Login
        from ptah import authentication
        self.init_ptah()

        config.get_cfg_storage(
            authentication.AUTH_PROVIDER_ID)['test'] = Provider()
        request = DummyRequest(params = {'login': 'admin', 'password': '12345'})

        login = Login(request)
        info = json.loads(login().text)

        self.assertIn('auth-token', info)
        self.assertEqual(request.response.status, '200 OK')

    def test_rest_api_auth(self):
        from ptah.rest import Api, Login
        from ptah import authentication
        self.init_ptah()

        config.get_cfg_storage(
            authentication.AUTH_PROVIDER_ID)['test'] = Provider()

        request = DummyRequest(
            params = {'login': 'admin', 'password': '12345'})

        login = Login(request)
        info = json.loads(login().text)

        request = DummyRequest(environ = {'HTTP_X_AUTH_TOKEN': 'unknown'})
        request.matchdict = {'service': 'cms', 'subpath': ()}

        result = Api(request)
        self.assertEqual(ptah.auth_service.get_userid(), None)

        token = info['auth-token']

        request = DummyRequest(environ = {'HTTP_X_AUTH_TOKEN': token})
        request.matchdict = {'service': 'cms', 'subpath': ()}

        result = Api(request)
        self.assertEqual(ptah.auth_service.get_userid(), 'testprincipal:1')


class TestRestApi(PtahTestCase):

    _init_ptah = False

    def test_rest_unknown_service(self):
        from ptah.rest import Api
        self.init_ptah()

        request = DummyRequest()
        request.matchdict = {'service': 'test', 'subpath': ()}

        res = json.loads(Api(request).text)
        self.assertEqual(res['message'], "'test'")
        self.assertIn("KeyError: 'test'", res['traceback'])

    def test_rest_arguments(self):
        from ptah.rest import Api, ID_REST
        self.init_ptah()

        services = config.get_cfg_storage(ID_REST)

        data = []
        def service(request, action, *args):
            data[:] = [action, args]

        services['test'] = service

        request = DummyRequest()
        request.matchdict = {'service': 'test',
                             'subpath': ('action:test','1','2')}

        api = Api(request)

        self.assertEqual(data[0], "action")
        self.assertEqual(data[1], ('test', '1', '2'))

    def test_rest_httpexception(self):
        from ptah.rest import Api, ID_REST
        self.init_ptah()

        services = config.get_cfg_storage(ID_REST)

        def service(request, action, *args):
            raise HTTPNotFound()

        services['test'] = service

        request = DummyRequest()
        request.matchdict = {'service': 'test',
                             'subpath': ('action:test','1','2')}

        res = json.loads(Api(request).text)
        self.assertEqual(
            res['message'], 'The resource could not be found.')

    def test_rest_response(self):
        from ptah.rest import Api, ID_REST
        self.init_ptah()

        services = config.get_cfg_storage(ID_REST)

        def service(request, action, *args):
            return HTTPNotFound()

        services['test'] = service

        request = DummyRequest(registry=self.config.registry)
        request.matchdict = {'service': 'test',
                             'subpath': ('action:test','1','2')}
        res = Api(request)
        self.assertIsInstance(res, HTTPNotFound)

    def test_rest_response_data(self):
        import datetime
        from ptah.rest import Api, ID_REST
        self.init_ptah()

        services = config.get_cfg_storage(ID_REST)

        def service(request, action, *args):
            return {'dt': datetime.datetime.now()}

        services['test'] = service

        request = DummyRequest()
        request.matchdict = {'service': 'test',
                             'subpath': ('action:test','1','2')}

        res = json.loads(Api(request).text)
        self.assertIn('dt', res)
