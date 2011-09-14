# ptah rest api
from memphis import view
from simplejson import dumps
from collections import OrderedDict

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

class Api(object):
    view.pyramidView(route='ptah-rest', layout=None)

    def __init__(self, request):
        self.request = request

    def render(self):
        request = self.request

        service = request.matchdict['service']
        subpath = request.matchdict['subpath']
        if subpath:
            action = subpath[0]
            arguments = subpath[1:]
        else:
            action = 'apidoc'
            arguments = ()

        request.response.headerslist = {'Content-Type': 'application/json'}
        return '%s\n\n'%dumps(
            services[service](request, action, *arguments), 
            indent=True)
