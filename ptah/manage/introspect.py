""" introspect module """
import inspect, sys
import urllib
from pyramid.compat import string_types
from pyramid.interfaces import IRoutesMapper, IRouteRequest
from pyramid.interfaces import IViewClassifier, IExceptionViewClassifier

from zope import interface
from zope.interface.interface import InterfaceClass

import ptah
from ptah import config, view, manage, form
from ptah.manage import intr_renderer, get_manage_url
from ptah.manage.manage import INTROSPECT_ID


@manage.module('introspect')
class IntrospectModule(manage.PtahModule):
    __doc__ = 'Insight into all configuration and registrations.'

    title = 'Introspect'

    packages = None

    def list_packages(self):
        if self.packages is None:
            self.packages = sorted(config.list_packages())

        return self.packages

    def __getitem__(self, key):
        key = urllib.unquote(key)
        packages = self.list_packages()
        if key in packages:
            return Package(key, self, self.request)

        if key in self.request.registry.introspector.categories():
            return Introspector(key, self, self.request)

        raise KeyError(key)


class Package(object):

    def __init__(self, pkg, mod, request):
        self.__name__ = pkg
        self.__parent__ = mod

        self.pkg = pkg
        self.request = request

    def actions(self):
        actions = config.scan(self.pkg, set(), config.exclude)

        info = {}

        for action in actions:
            d = action.discriminator[0]
            d_data = info.setdefault(d, {})
            mod_data = d_data.setdefault(action.info.module.__name__, [])
            mod_data.append(action)

        return info


class Introspector(object):

    def __init__(self, name, mod, request):
        self.__name__ = name
        self.__parent__ = mod

        self.name = name
        self.request = request

        intros = config.get_cfg_storage(INTROSPECT_ID)
        self.renderer = intros[name](request)

        self.intrs = sorted((item['introspectable'] for item in
                             self.request.registry
                             .introspector.get_category(name)),
                            key = lambda item: item.title)

        self.manage_url = '{0}/introspect'.format(get_manage_url(self.request))
        self.renderers = sorted(
            (item['introspectable']['factory'] for item in
             self.request.registry.introspector.get_category(INTROSPECT_ID)),
            key = lambda item: item.title)


class MainView(view.View):
    view.pview(
        context = IntrospectModule,
        template = view.template('ptah.manage:templates/introspect.pt'))

    __doc__ = 'Introspection module view.'
    __intr_path__ = '/ptah-manage/introspect/index.html'

    def update(self):
        self.packages = self.context.list_packages()
        self.manage_url = '{0}/introspect'.format(get_manage_url(self.request))
        self.renderers = sorted(
            (item['introspectable']['factory'] for item in
             self.request.registry.introspector.get_category(INTROSPECT_ID)),
            key = lambda item: item.title)


class PackageView(view.View):
    view.pview(
        context = Package,
        template = view.template('ptah.manage:templates/introspect-pkg.pt'))

    __doc__ = 'Package introspection page.'
    __intr_path__ = '/ptah-manage/introspect/${pkg}/index.html'

    def update(self):
        self.data = self.context.actions()

        self.ndata = ndata = {}
        for tp, d in self.data.items():
            actions = []
            for k, ac in d.items():
                actions.extend(ac)

            ndata[tp] = actions

        itypes = []
        intros = config.get_cfg_storage(INTROSPECT_ID)
        for key, cls in intros.items():
            if key in self.data:
                itypes.append((cls.title, cls(self.request)))

        self.itypes = [it for _t, it in sorted(itypes)]


class IntrospectorView(view.View):
    view.pview(
        context = Introspector,
        template = view.template('ptah.manage:templates/introspect-intr.pt'))



def lineno(ob):
    if ob is not None:
        return inspect.getsourcelines(ob)[-1]


class EventsView(view.View):
    view.pview(
        'events.html', IntrospectModule,
        template = view.template('ptah.manage:templates/introspect-events.pt'))

    __doc__ = 'Events introspection page.'
    __intr_path__ = '/ptah-manage/introspect/events.html'

    events = None
    actions = None
    lineno = staticmethod(lineno)

    def update(self):
        ev = self.request.params.get('ev')

        all_events = config.get_cfg_storage(config.ID_EVENT)
        self.event = event = all_events.get(ev)

        if event is None:
            events = []
            for n, ev in all_events.items():
                if isinstance(n, string_types):
                    events.append((ev.title, ev))

            self.events = [ev for _t, ev in sorted(events)]
        else:
            pkgs = config.list_packages()
            evinst = event.instance

            seen = set()
            actions = []
            for pkg in pkgs:
                for action in config.scan(pkg, seen, config.exclude):
                    if action.discriminator[0] == config.ID_SUBSCRIBER:
                        required = action.args[1]
                        if len(required) == 2 and required[1] == evinst:
                            actions.append(action)
                        elif required[0] == evinst:
                            actions.append(action)

            self.actions = actions


class RoutesView(view.View):
    view.pview(
        'routes.html', IntrospectModule,
        template = view.template('ptah.manage:templates/introspect-routes.pt'))

    __doc__ = 'Routes introspection page.'
    __intr_path__ = '/ptah-manage/introspect/routes.html'

    def update(self):
        self.route = route = None

        if route is None:
            packages = config.list_packages()

            viewactions = []

            seen = set()
            routes = {}
            for pkg in packages:
                actions = config.scan(pkg, seen, config.exclude)

                for action in actions:
                    d = action.discriminator[0]
                    if d == 'ptah.view:route':
                        name, pattern, factory = action.args[:3]
                        routes[name] = (pattern, name, factory, [])
                    elif d == 'ptah.view:view':
                        factory = action.info.context
                        if inspect.isclass(factory):
                            isclass = True
                            name = action.args[0]
                            context = action.args[1]
                            route = action.args[3]
                        else:
                            factory = action.args[0]
                            name = action.args[1]
                            context = action.args[2]
                            route = action.args[4]
                        if route:
                            viewactions.append(
                                (route, name, context, factory, action))

            sm = self.request.registry

            # add pyramid routes
            for route in sm.getUtility(IRoutesMapper).get_routes():
                if route.name not in routes:
                    routes[route.name] = (
                        route.pattern, route.name, route.factory, [])

            # attach views to routes
            for route, name, context, factory, action in viewactions:
                try:
                    rdata = routes[route][3]
                except: # pragma: no cover
                    continue
                rdata.append([getattr(factory, '__intr_path__', name),
                              action.info.module.__name__, lineno(factory),
                              factory, action.discriminator[-1]])
                rdata = sorted(rdata)

            self.routes = sorted(routes.values())

            # views
            route_requests = [i for n, i in sm.getUtilitiesFor(IRouteRequest)]

            views = []
            data = sm.adapters._adapters[3]
            for classifier, data in data.items():
                if classifier in (IViewClassifier, IExceptionViewClassifier):
                    for req, data2 in data.items():
                        if req in route_requests:
                            continue

                        for context, data3 in data2.items():
                            if isinstance(context, InterfaceClass):
                                context = '%s.%s'%(
                                    context.__module__, context.__name__)
                            else:
                                context = context.__name__

                            for provides, adapters in data3.items():
                                for name, factory in adapters.items():
                                    views.append(
                                        (context,name,classifier,req,factory))

            self.views = sorted(views)
