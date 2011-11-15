import ptah
import simplejson
from ptah import config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPNotFound

from base import Base


class TestRestRegistrations(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestRestRegistrations, self).tearDown()

    def test_rest_registerService(self):
        import ptah.rest

        srv = ptah.rest.RestService('test', 'Test service')
        self._init_ptah()

        services = config.get_cfg_storage(ptah.rest.REST_ID)

        self.assertEqual(srv.name, 'test')
        self.assertIn('test', services)
        self.assertIn(srv, services.values())

    def test_rest_registerService_conflicts(self):
        import ptah.rest

        ptah.rest.RestService('test', 'Test service')
        ptah.rest.RestService('test', 'Test service2')

        self.assertRaises(config.ConflictError, self._init_ptah)

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
        self._init_ptah()

        srv = config.get_cfg_storage(ptah.rest.REST_ID)['test']

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
            info['actions'][0]['__link__'], 'http://localhost:8080/apidoc')
        self.assertEqual(info['actions'][1]['name'], 'action')
        self.assertEqual(
            info['actions'][1]['__link__'], 'http://localhost:8080/action')


class Principal(object):
    uri = 'testprincipal:1'
    name = 'admin'
    login = 'admin'


class Provider(object):
    principal = Principal()

    def authenticate(self, creds):
        return self.principal


class TestRestView(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestRestView, self).tearDown()

    def test_rest_enable_api(self):
        from ptah.rest import RestLoginRoute, RestApiRoute

        mapper = self.p_config.get_routes_mapper()

        self.assertIsNone(mapper.get_route('ptah-rest'))
        self.assertIsNone(mapper.get_route('ptah-rest-login'))

        ptah.enable_rest_api(self.p_config)

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

        self.assertIn('authentication failed', login.render())
        self.assertEqual(request.response.status, '403 Forbidden')

    def test_rest_login_success(self):
        from ptah.rest import Login
        from ptah import authentication
        self._init_ptah()

        config.get_cfg_storage(
            authentication.AUTH_PROVIDER_ID)['test'] = Provider()
        request = DummyRequest(params = {'login': 'admin', 'password': '12345'})

        login = Login(request)
        info = simplejson.loads(login.render())

        self.assertIn('auth-token', info)
        self.assertEqual(request.response.status, '200 OK')

    def test_rest_api_auth(self):
        from ptah.rest import Api, Login
        from ptah import authentication
        self._init_ptah()

        config.get_cfg_storage(
            authentication.AUTH_PROVIDER_ID)['test'] = Provider()

        request = DummyRequest(params = {'login': 'admin', 'password': '12345'})

        login = Login(request)
        info = simplejson.loads(login.render())

        request = DummyRequest(environ = {'HTTP_X_AUTH_TOKEN': 'unknown'})
        request.matchdict = {'service': 'cms', 'subpath': ()}

        api = Api(request)
        api.render()
        self.assertEqual(ptah.authService.get_userid(), None)

        token = info['auth-token']

        request = DummyRequest(environ = {'HTTP_X_AUTH_TOKEN': token})
        request.matchdict = {'service': 'cms', 'subpath': ()}

        api = Api(request)
        api.render()
        self.assertEqual(ptah.authService.get_userid(), 'testprincipal:1')


class TestRestApi(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestRestApi, self).tearDown()

    def test_rest_unknown_service(self):
        from ptah.rest import Api
        self._init_ptah()

        request = DummyRequest()
        request.matchdict = {'service': 'test', 'subpath': ()}

        api = Api(request)
        res = simplejson.loads(api.render())
        self.assertEqual(res['message'], "'test'")
        self.assertIn("KeyError: 'test'", res['traceback'])

    def test_rest_arguments(self):
        from ptah.rest import Api, REST_ID
        self._init_ptah()

        services = config.get_cfg_storage(REST_ID)

        data = []
        def service(request, action, *args):
            data[:] = [action, args]

        services['test'] = service

        request = DummyRequest()
        request.matchdict = {'service': 'test',
                             'subpath': ('action:test','1','2')}

        api = Api(request)
        api.render()

        self.assertEqual(data[0], "action")
        self.assertEqual(data[1], ('test', '1', '2'))

    def test_rest_httpexception(self):
        from ptah.rest import Api, REST_ID
        self._init_ptah()

        services = config.get_cfg_storage(REST_ID)

        def service(request, action, *args):
            raise HTTPNotFound()

        services['test'] = service

        request = DummyRequest()
        request.matchdict = {'service': 'test',
                             'subpath': ('action:test','1','2')}
        api = Api(request)
        res = simplejson.loads(api.render())
        self.assertEqual(
            res['message'], 'The resource could not be found.')

    def test_rest_response(self):
        from ptah.rest import Api, REST_ID
        self._init_ptah()

        services = config.get_cfg_storage(REST_ID)

        def service(request, action, *args):
            return HTTPNotFound()

        services['test'] = service

        request = DummyRequest(registry=self.p_config.registry)
        request.matchdict = {'service': 'test',
                             'subpath': ('action:test','1','2')}
        api = Api(request)
        res = api.render()
        self.assertIsInstance(res, HTTPNotFound)

    def test_rest_response_data(self):
        import datetime
        from ptah.rest import Api, REST_ID
        self._init_ptah()

        services = config.get_cfg_storage(REST_ID)

        def service(request, action, *args):
            return {'dt': datetime.datetime.now()}

        services['test'] = service

        request = DummyRequest()
        request.matchdict = {'service': 'test',
                             'subpath': ('action:test','1','2')}
        api = Api(request)
        res = simplejson.loads(api.render())
        self.assertIn('dt', res)
