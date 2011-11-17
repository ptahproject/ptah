""" ptah rest api """
import traceback
from datetime import datetime
from cStringIO import StringIO
from simplejson import dumps
from collections import OrderedDict
from pyramid.response import Response
from pyramid.authentication import parse_ticket, AuthTicket, BadTicket
from pyramid.httpexceptions import WSGIHTTPException, HTTPNotFound

from ptah import view, config

import ptah
from ptah.settings import SECURITY


REST_ID = 'ptah:rest-service'


def RestService(name, title, description=''):
    srv = Service(name, title, description)

    apidoc = ServiceAPIDoc(name)
    srv.actions['apidoc'] = Action(apidoc, 'apidoc', apidoc.title)

    def _register(cfg, srv):
        cfg.get_cfg_storage(REST_ID)[name] = srv

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            _register, (srv, ),
            discriminator=(REST_ID, name))
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
        srv = config.get_cfg_storage(REST_ID)[self.srvname]
        url = request.application_url

        info = OrderedDict(
            (('name', srv.name),
             ('__link__', '%s/' % url),
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
                     ('__link__', '%s/%s' % (url, name)),
                     ('title', title),
                     ('description', description))))

        return info


class RestLoginRoute(object):
    """ rest login route """

    def __init__(self, request):
        self.request = request


class RestApiRoute(object):
    """ rest api route """

    def __init__(self, request):
        self.request = request


def dthandler(obj):
    return obj.isoformat() if isinstance(obj, datetime) else None


class Login(object):
    view.pview(context=RestLoginRoute)

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
        return '%s\n\n' % dumps(result, indent=True, default=dthandler)

    def get_token(self, request, userid):
        secret = SECURITY.secret
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
    view.pview(context=RestApiRoute)

    def __init__(self, request):
        self.request = request

    def render(self):
        request = self.request

        # authentication by token
        token = request.environ.get('HTTP_X_AUTH_TOKEN')
        if token:
            try:
                timestamp, userid, tokens, user_data = parse_ticket(
                    SECURITY.secret,
                    '%s!' % token,
                    '0.0.0.0')
            except BadTicket:
                userid = None

            if userid:
                ptah.authService.set_userid(userid)

        # search service and action
        service = request.matchdict['service']
        subpath = request.matchdict['subpath']
        if subpath:
            action = subpath[0]
            arguments = subpath[1:]
            if ':' in action:
                action, arg = action.split(':', 1)
                arguments = (arg,) + arguments
        else:
            action = 'apidoc'
            arguments = ()

        request.environ['SCRIPT_NAME'] = '/__rest__/%s' % service
        request.response.headerslist = {'Content-Type': 'application/json'}

        # execute action for specific service
        try:
            result = config.get_cfg_storage(REST_ID)[service](
                request, action, *arguments)
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

        return '%s\n\n' % dumps(result, indent=True, default=dthandler)


def enable_rest_api(config):
    """ Register /__rest__/login and /__rest__/{service}/*subpath
    routes """

    config.add_route(
        'ptah-rest-login', '/__rest__/login',
        factory=RestLoginRoute, use_global_views=True)

    config.add_route(
        'ptah-rest', '/__rest__/{service}/*subpath',
        factory=RestApiRoute, use_global_views=True)
