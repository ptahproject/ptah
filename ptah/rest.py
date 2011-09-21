# ptah rest api
import traceback
from memphis import view
from datetime import datetime
from simplejson import dumps
from collections import OrderedDict
from cStringIO import StringIO
from pyramid.authentication import AuthTicket
from pyramid.httpexceptions import WSGIHTTPException, HTTPServerError
from pyramid.interfaces import IAuthenticationPolicy

from ptah import security

__all__ = ['registerService', 'registerServiceAction', 'Action']


services = {}


def registerService(name, title, description):
    services[name] = Service(name, title, description)
    services[name].registerAction(ServiceAPIDoc(name))


def registerServiceAction(name, action):
    services[name].registerAction(action)


class RestException(HTTPServerError):
    """ rest exception """
    

class Service(object):

    def __init__(self, name, title, description):
        self.name = name
        self.title = title
        self.description = description
        self.actions = {}

    def registerAction(self, action):
        self.actions[action.name] = action

    def __call__(self, request, action, *args):
        action = self.actions.get(action)
        if action:
            return action(request, *args)
    

class Action(object):

    name = ''
    title = ''
    description = ''

    def __call__(self, request, *args):
        raise NotImplemented()


class ServiceAPIDoc(Action):

    name='apidoc'
    title = 'API Doc'

    def __init__(self, name):
        self.srvname = name

    def __call__(self, request):
        srv = services[self.srvname]
        url = request.application_url

        info = OrderedDict(
            (('name', srv.name),
             ('link', '%s/'%url),
             ('title', srv.title),
             ('description', srv.description),
             ('actions', [])))

        actions = [(a.title, a.name, a.description) 
                   for a in srv.actions.values()]
        actions.sort()
        
        for title, name, description in actions:
            info['actions'].append(
                OrderedDict(
                    (('name', name),
                     ('link', '%s/%s'%(url, name)), 
                     ('title', title),
                     ('description', description))))

        return info


view.registerRoute(
    'ptah-rest-login', '/__api__/login')

view.registerRoute(
    'ptah-rest', '/__api__/{service}/*subpath', use_global_views=True)


def dthandler(obj):
    return obj.isoformat() if isinstance(obj, datetime) else None


class Login(object):
    view.pyramidView(route='ptah-rest-login', layout=None)

    def __init__(self, request):
        self.request = request

    def render(self):
        request = self.request
        
        login = request.POST.get('login', '')
        password = request.POST.get('password', '')

        credentials = {'login': login, 'password': password}
        info = security.authService.authenticate(credentials)
        if info.status:
            token = self.get_token(request, info.uuid)
            result = {'status': True, 'message': '', 'auth-token': token[:-1]}
        else:
            request.response.status = 403
            result = {'status': False, 'message': info.message}

        return '%s\n\n'%dumps(result, indent=True, default=dthandler)

    def get_token(self, request, userid):
        auth = request.registry.getUtility(IAuthenticationPolicy)

        cookie = auth.cookie
        environ = request.environ
        remote_addr = '0.0.0.0'

        ticket = AuthTicket(
            cookie.secret,
            userid,
            remote_addr,
            tokens=(),
            user_data='',
            cookie_name='auth-token',
            secure=False)

        return ticket.cookie_value()


class Api(object):
    view.pyramidView(route='ptah-rest', layout=None)

    def __init__(self, request):
        self.request = request

    def render(self):
        request = self.request

        # authentication by token
        token = request.environ.get('HTTP_X_AUTH_TOKEN')
        if token:
            auth = request.registry.getUtility(IAuthenticationPolicy)
            try:
                timestamp, userid, tokens, user_data = auth.cookie.parse_ticket(
                    auth.cookie.secret, '%s!'%token, '0.0.0.0')
            except auth.cookie.BadTicket:
                userid = None

            if userid:
                security.authService.setUserId(userid)

        # search service and action
        service = request.matchdict['service']
        subpath = request.matchdict['subpath']
        if subpath:
            action = subpath[0]
            arguments = subpath[1:]
            if ':' in action:
                action, arg = action.split(':',1)
                arguments = (arg,) + arguments
        else:
            action = 'apidoc'
            arguments = ()

        request.environ['SCRIPT_NAME'] = '/__api__/%s'%service
        request.response.headerslist = {'Content-Type': 'application/json'}

        # execute action for specific service
        try:
            result = services[service](request, action, *arguments)
        except WSGIHTTPException, exc:
            request.response.status = exc.status
            result = {'code': exc.status,
                      'message': str(exc)}
        except Exception, exc:
            request.response.status = 500

            out = StringIO()
            traceback.print_exc(file=out)

            result = {'code': request.response.status,
                      'message': str(exc),
                      'traceback': out.getvalue()}

        return '%s\n\n'%dumps(result, indent=True, default=dthandler)
