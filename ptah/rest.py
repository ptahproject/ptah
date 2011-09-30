""" ptah rest api """
import traceback
from datetime import datetime
from cStringIO import StringIO
from simplejson import dumps
from collections import OrderedDict
from pyramid.response import Response
from pyramid.authentication import AuthTicket
from pyramid.httpexceptions import \
    WSGIHTTPException, HTTPServerError, HTTPNotFound
from pyramid.interfaces import IAuthenticationPolicy
from memphis import view, config

import ptah
from ptah.app import SECURITY


services = {}

def restService(name, title, description=''):
    srv = Service(name, title, description)
    apidoc = ServiceAPIDoc(name)

    services[name] = srv
    srv.actions['apidoc'] = Action(apidoc, 'apidoc', apidoc.title)

    def _register(srv):
        services[name] = srv

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            _register, (srv,),
            discriminator = ('ptah:rest-service', id))
        )

    return srv


class Action(object):

    def __init__(self, callable, name, title):
        self.name = name
        self.title = title
        self.callable = callable
        self.description = callable.__doc__ or ''


class Service(object):

    def __init__(self, name, title, description):
        self.name = name
        self.title = title
        self.description = description
        self.actions = {}

    def action(self, name, title):
        info = config.DirectiveInfo()

        def wrapper(func):
            self.actions[name] = Action(func, name, title)
            return func

        return wrapper

    def __call__(self, request, action, *args):
        action = self.actions.get(action)
        if action:
            return action.callable(request, *args)
        else:
            raise HTTPNotFound


class ServiceAPIDoc(object):

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
    'ptah-rest-login', '/__rest__/login')

view.registerRoute(
    'ptah-rest', '/__rest__/{service}/*subpath', use_global_views=True)


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
        info = ptah.authService.authenticate(credentials)
        if info.status:
            token = self.get_token(request, info.uri)
            result = {'message': '', 'auth-token': token[:-1]}
        else:
            request.response.status = 403
            result = {'message': info.message or 'authentication failed'}

        request.response.headerslist = {'Content-Type': 'application/json'}
        return '%s\n\n'%dumps(result, indent=True, default=dthandler)

    def get_token(self, request, userid):
        secret = SECURITY.secret
        environ = request.environ
        remote_addr = '0.0.0.0'

        ticket = AuthTicket(
            secret,
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
                ptah.authService.setUserId(userid)

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

        request.environ['SCRIPT_NAME'] = '/__rest__/%s'%service
        request.response.headerslist = {'Content-Type': 'application/json'}

        # execute action for specific service
        try:
            result = services[service](request, action, *arguments)
        except WSGIHTTPException, exc:
            request.response.status = exc.status
            result = {'message': str(exc)}
        except Exception, exc:
            request.response.status = 500

            out = StringIO()
            traceback.print_exc(file=out)

            result = {'message': str(exc),
                      'traceback': out.getvalue()}

        if isinstance(result, Response):
            return result

        return '%s\n\n'%dumps(result, indent=True, default=dthandler)
