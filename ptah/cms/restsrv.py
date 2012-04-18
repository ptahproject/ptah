""" ptah rest api """
import traceback
from datetime import datetime
from json import dumps
from collections import OrderedDict
from pyramid.view import view_config
from pyramid.compat import NativeIO, text_
from pyramid.response import Response
from pyramid.authentication import parse_ticket, AuthTicket, BadTicket
from pyramid.httpexceptions import WSGIHTTPException, HTTPNotFound

import ptah
from ptah import config


ID_REST = 'ptah:rest-service'


def RestService(name, title, description=''):
    srv = Service(name, title, description)

    apidoc = ServiceAPIDoc(name)
    srv.actions['apidoc'] = Action(apidoc, 'apidoc', apidoc.title)

    def _register(cfg, srv):
        cfg.get_cfg_storage(ID_REST)[name] = srv

    discr = (ID_REST, name)
    intr = config.Introspectable(ID_REST, discr, name, ID_REST)
    intr['service'] = srv

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            _register, (srv,), discriminator=discr, introspectables=(intr,))
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
            raise HTTPNotFound()


class ServiceAPIDoc(object):

    title = 'API Doc'

    def __init__(self, name):
        self.srvname = name

    def __call__(self, request):
        srv = ptah.get_cfg_storage(ID_REST)[self.srvname]
        url = request.application_url

        info = OrderedDict(
            (('name', srv.name),
             ('__link__', '%s/' % url),
             ('title', srv.title),
             ('description', srv.description),
             ('actions', [])))

        actions = [(a.title, a.name, a.description)
                   for a in srv.actions.values()]

        for title, name, description in sorted(actions):
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


@view_config(context=RestLoginRoute)
class Login(object):
    """ Rest login view """

    def __init__(self, request):
        self.request = request

    def __call__(self):
        request = self.request
        response = request.response

        login = request.POST.get('login', '')
        password = request.POST.get('password', '')

        credentials = {'login': login, 'password': password}
        info = ptah.auth_service.authenticate(credentials)
        if info.status:
            token = self.get_token(request, info.__uri__)
            result = {'message': '', 'auth-token': token[:-1]}
        else:
            response.status = 403
            result = {'message': info.message or 'authentication failed'}

        response.headerslist = {'Content-Type': 'application/json'}
        response.text = text_(
            dumps(result, indent=True, default=dthandler), 'utf-8')
        return response

    def get_token(self, request, userid):
        secret = ptah.get_settings(
            ptah.CFG_ID_PTAH, request.registry)['secret']
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


@view_config(context=RestApiRoute)
def Api(request):
    """ Rest API interface """
    response = request.response

    # authentication by token
    token = request.environ.get('HTTP_X_AUTH_TOKEN')
    if token:
        secret = ptah.get_settings(ptah.CFG_ID_PTAH, request.registry)['secret']

        try:
            timestamp, userid, tokens, user_data = parse_ticket(
                secret, '%s!' % token, '0.0.0.0')
        except BadTicket:
            userid = None

        if userid:
            ptah.auth_service.set_userid(userid)

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
    response.headerslist = {'Content-Type': 'application/json'}

    # execute action for specific service
    try:
        result = config.get_cfg_storage(ID_REST)[service](
            request, action, *arguments)
    except WSGIHTTPException as exc:
        response.status = exc.status
        result = {'message': str(exc)}
    except Exception as exc:
        response.status = 500

        out = NativeIO()
        traceback.print_exc(file=out)

        result = {'message': str(exc),
                  'traceback': out.getvalue()}

    if isinstance(result, Response):
        return result

    response.text = text_(
        dumps(result, indent=True, default=dthandler), 'utf-8')
    return response


def enable_rest_api(config):
    """Register /__rest__/login and /__rest__/{service}/*subpath routes."""

    config.add_route(
        'ptah-rest-login', '/__rest__/login',
        factory=RestLoginRoute, use_global_views=True)

    config.add_route(
        'ptah-rest', '/__rest__/{service}/*subpath',
        factory=RestApiRoute, use_global_views=True)
