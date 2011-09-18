# ptah rest api
import traceback
from memphis import view
from datetime import datetime
from simplejson import dumps
from collections import OrderedDict
from cStringIO import StringIO
from pyramid.security import remember, forget
from pyramid.httpexceptions import WSGIHTTPException

from ptah import security

__all__ = ['registerService', 'registerServiceAction', 'Action']


services = {}


def registerService(name, title, description):
    services[name] = Service(name, title, description)
    services[name].registerAction(ServiceAPIDoc(name))


def registerServiceAction(name, action):
    services[name].registerAction(action)


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
        url = '%s/__api__/'%request.application_url

        info = OrderedDict(
            (('name', srv.name),
             ('link', '%s%s/'%(url, srv.name)),
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
                     ('link', '%s%s/%s'%(url, srv.name, name)), 
                     ('title', title),
                     ('description', description))))

        return info


view.registerRoute(
    'ptah-rest', '/__api__/{service}/*subpath', use_global_views=True)


def dthandler(obj):
    return obj.isoformat() if isinstance(obj, datetime) else None


class Api(object):
    view.pyramidView(route='ptah-rest', layout=None)

    def __init__(self, request):
        self.request = request

    def login(self):
        request = self.request
        
        login = request.POST.get('login', '')
        password = request.POST.get('password', '')

        credentials = {'login': login, 'password': password}
        info = security.authService.authenticate(credentials)
        if info.status:
            headers = remember(request, info.uuid)
            request.response.headerslist = headers
            return {'status': True, 'message': '',
                    'cookie': headers[0][1]}
        else:
            request.response.status = 403
            return {'status': False, 'message': info.message}

    def render(self):
        request = self.request

        service = request.matchdict['service']
        if service == 'login':
            res = self.login()
            return '%s\n\n'%dumps(res, indent=True, default=dthandler)
        
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
