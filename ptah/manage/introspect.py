""" introspect module """
import pkg_resources, inspect, os, sys
from pyramid.interfaces import IRoutesMapper, IRouteRequest
from pyramid.interfaces import IViewClassifier, IExceptionViewClassifier

from zope import interface
from zope.interface.interface import InterfaceClass

import ptah
from ptah import config, view, manage, form
from ptah.uri import RESOLVER_ID
from ptah.config import directives
from ptah.config.api import exclude, list_packages

from manage import INTROSPECTIONS


class IntrospectModule(manage.PtahModule):
    __doc__ = u'Insight into all configuration and registrations.'

    title = 'Introspect'
    manage.module('introspect')

    packages = None

    def list_packages(self):
        if self.packages is None:
            self.packages = list_packages()
            self.packages.sort()
        return self.packages

    def __getitem__(self, key):
        packages = self.list_packages()
        if key in packages:
            return Package(key, self, self.request)

        raise KeyError(key)


class Package(object):

    def __init__(self, pkg, mod, request):
        self.__name__ = pkg
        self.__parent__ = mod

        self.pkg = pkg
        self.request = request

    def actions(self):
        actions = directives.scan(self.pkg, set(), exclude)

        info = {}

        for action in actions:
            d = action.discriminator[0]
            d_data = info.setdefault(d, {})
            mod_data = d_data.setdefault(action.info.module.__name__, [])
            mod_data.append(action)

        return info


class MainView(view.View):
    view.pview(
        context = IntrospectModule,
        template = view.template('ptah.manage:templates/introspect.pt'))

    __doc__ = 'Introspection module view.'
    __intr_path__ = '/ptah-manage/introspect/index.html'

    def update(self):
        self.packages = self.context.list_packages()


class UriResolver(form.Form):
    view.pview('uri.html', context = IntrospectModule,
               template = view.template('ptah.manage:templates/uri.pt'))

    fields = form.Fieldset(
        form.LinesField(
            'uri',
            title = 'Uri',
            description = "List of uri's",
            klass = 'xxlarge'))

    uri = None

    def form_content(self):
        return {'uri': [self.request.GET.get('uri','')]}

    @form.button('Show', actype=form.AC_PRIMARY)
    def showHandler(self):
        data, errors = self.extract()
        if errors:
            self.message(errors, 'form-error')
        else:
            self.uri = data['uri']

    def update(self):
        super(UriResolver, self).update()

        uri = self.uri
        if uri is None:
            uri = [self.request.GET.get('uri','')]

        resolvers = config.registry.storage[RESOLVER_ID]

        self.data = data = []
        for u in uri:
            if u:
                schema = ptah.extract_uri_schema(u)
                resolver = resolvers.get(schema)
                info = {'uri': u,
                        'resolver': None,
                        'module': None,
                        'line': None,
                        'obj': None,
                        'cls': None,
                        'clsdoc': None}

                if resolver is not None:
                    info['resolver'] = resolver.__doc__ or resolver.__name__
                    info['module'] = resolver.__module__
                    info['name'] = '%s.%s'%(
                        resolver.__module__, resolver.__name__)
                    info['line'] = inspect.getsourcelines(resolver)[-1]

                    obj = ptah.resolve(u)
                    info['obj'] = obj

                    cls = getattr(obj, '__class__', None)
                    info['cls'] = cls
                    info['clsdoc'] = getattr(cls, '__doc__', '')

                    if cls is not None:
                        info['clsmod'] = cls.__module__
                        info['clsline'] = inspect.getsourcelines(cls)[-1]

                data.append(info)


view.register_snippet(
    'ptah-module-actions', IntrospectModule,
    template = view.template('ptah.manage:templates/introspect-actions.pt'))


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
        for key, cls in INTROSPECTIONS.items():
            if key in self.data:
                itypes.append((cls.title, cls(self.request)))

        itypes.sort()
        self.itypes = [it for _t, it in itypes]


class EventsView(view.View):
    view.pview(
        'events.html', IntrospectModule,
        template = view.template('ptah.manage:templates/introspect-events.pt'))

    __doc__ = 'Events introspection page.'
    __intr_path__ = '/ptah-manage/introspect/events.html'

    events = None
    actions = None

    def lineno(self, ob):
        return inspect.getsourcelines(ob)[-1]

    def update(self):
        ev = self.request.params.get('ev')

        all_events = config.registry.storage[directives.EVENT_ID]
        self.event = event = all_events.get(ev)

        if event is None:
            events = []
            for n, ev in all_events.items():
                if isinstance(n, basestring):
                    events.append((ev.title, ev))

            events.sort()
            self.events = [ev for _t, ev in events]
        else:
            pkgs = list_packages()
            evinst = event.instance

            seen = set()
            actions = []
            for pkg in pkgs:
                for action in directives.scan(pkg, seen, exclude):
                    if action.discriminator[0] == 'ptah.config:subscriber':
                        required = action.args[2]
                        if len(required) == 2 and required[1] == evinst:
                            actions.append(action)
                        elif required[0] == evinst:
                            actions.append(action)

            self.actions = actions


def lineno(ob):
    if ob is not None:
        return inspect.getsourcelines(ob)[-1]


class RoutesView(view.View):
    view.pview(
        'routes.html', IntrospectModule,
        template = view.template('ptah.manage:templates/introspect-routes.pt'))

    __doc__ = 'Routes introspection page.'
    __intr_path__ = '/ptah-manage/introspect/routes.html'

    def update(self):
        #ev = self.request.params.get('ev')
        self.route = route = None #directives.events.get(ev)

        if route is None:
            packages = list_packages()

            viewactions = []

            seen = set()
            routes = {}
            for pkg in packages:
                actions = directives.scan(pkg, seen, exclude)

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
                            isclass = False
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
                except:
                    continue
                rdata.append([getattr(factory, '__intr_path__', name),
                              action.info.module.__name__, lineno(factory),
                              factory, action.discriminator[-1]])
                rdata.sort()

            routes = routes.values()
            routes.sort()
            self.routes = routes

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

            views.sort()
            self.views = views


class SourceView(view.View):
    view.pview(
        'source.html', IntrospectModule,
        template = view.template('ptah.manage:templates/introspect-source.pt'))

    __doc__ = 'Source introspection page.'
    __intr_path__ = '/ptah-manage/introspect/source.html'

    source = None
    format = None

    def update(self):
        name = self.request.params.get('pkg')

        dist = None
        pkg_name = name
        while 1:
            try:
                dist = pkg_resources.get_distribution(pkg_name)
                if dist is not None:
                    break
            except pkg_resources.DistributionNotFound:
                if '.' not in pkg_name:
                    break
                pkg_name = pkg_name.rsplit('.',1)[0]

        if dist is None:
            self.source = None

        names = name[len(pkg_name)+1:].split('.')
        path = '%s.py'%os.path.join(*names)
        abspath = pkg_resources.resource_filename(pkg_name, path)

        if os.path.isfile(abspath):
            self.file = abspath
            self.name = '%s.py'%names[-1]
            self.pkg_name = pkg_name
            source = open(abspath, 'rb').read()

            if not self.format:
                from pygments import highlight
                from pygments.lexers import PythonLexer
                from pygments.formatters import HtmlFormatter

                html = HtmlFormatter(
                    linenos='inline',
                    lineanchors='sl',
                    anchorlinenos=True,
                    noclasses = True,
                    cssclass="ptah-source")

                def format(self, code, highlight=highlight,
                           lexer = PythonLexer()):
                    return highlight(code, lexer, html)
                self.__class__.format = format

            self.source = self.format(source)


class UriIntrospection(object):
    """ """

    title = 'Uri resolver'
    manage.introspection('ptah:uri-resolver')

    actions = view.template('ptah.manage:templates/directive-uriresolver.pt')

    def __init__(self, request):
        self.request = request

    def renderActions(self, *actions):
        return self.actions(
            resolvers = config.registry.storage[RESOLVER_ID],
            actions = actions,
            request = self.request)


class EventDirective(object):
    """ zca event declarations """

    title = 'Events'
    manage.introspection('ptah.config:event')

    actions = view.template('ptah.manage:templates/directive-event.pt')

    def __init__(self, request):
        self.request = request

    def renderActions(self, *actions):
        return self.actions(
            actions = actions,
            events = config.registry.storage[directives.EVENT_ID],
            request = self.request)


class AdapterDirective(object):
    """ zc adapter registrations """

    title = 'zc adapters'
    manage.introspection('ptah.config:adapter')

    actions = view.template('ptah.manage:templates/directive-adapter.pt')

    def __init__(self, request):
        self.request = request

    def getInfo(self, action):
        context = action.info.context

        if inspect.isclass(context):
            isclass = True
            requires, name = action.args[:2]
        else:
            context = action.args[1]
            requires = action.args[2]
            name = action.kw['name']

        provided = list(interface.implementedBy(context))
        if len(provided):
            iface = provided[0]
        else:
            iface = 'unknown'
        return locals()

    def renderActions(self, *actions):
        return self.actions(
            actions = actions,
            getInfo = self.getInfo,
            request = self.request)


class SnippetTypeDirective(object):
    """ ptah snippet types """

    title = 'Snippet Types'
    manage.introspection('ptah.view:snippettype')

    actions = view.template('ptah.manage:templates/directive-stype.pt')

    def __init__(self, request):
        self.request = request

    def renderActions(self, *actions):
        STYPE_ID = sys.modules['ptah.view.snippet'].STYPE_ID
        stypes = config.registry.storage[STYPE_ID]
        return self.actions(
            actions = actions,
            stypes = stypes,
            request = self.request)


class RouteDirective(object):
    """ pyramid routes """

    title = 'Routes'
    manage.introspection('ptah.view:route')

    actions = view.template('ptah.manage:templates/directive-route.pt')

    def __init__(self, request):
        self.request = request

    def renderActions(self, *actions):
        return self.actions(
            actions = actions,
            request = self.request)


class SubscriberDirective(object):
    """ zca event subscribers """

    title = 'Event subscribers'
    manage.introspection('ptah.config:subscriber')

    actions = view.template('ptah.manage:templates/directive-subscriber.pt')

    def __init__(self, request):
        self.request = request

    def getInfo(self, action):
        factory, ifaces = action.args[1:]
        factoryInfo = '%s.%s'%(action.info.module.__name__, factory.__name__)

        if len(action.args[2]) > 1:
            obj = action.args[2][0]
            klass = action.args[2][-1]
            event = config.registry.storage[directives.EVENT_ID].get(
                action.args[2][-1], None)
        else:
            obj = None
            klass = action.args[2][0]
            event = config.registry.storage[directives.EVENT_ID].get(
                action.args[2][0], None)

        return locals()

    def renderActions(self, *actions):
        return self.actions(
            getInfo = self.getInfo,
            actions = actions,
            request = self.request)


class ViewDirective(object):
    """ pyramid views """

    title = 'Views'
    manage.introspection('ptah.view:view')

    actions = view.template('ptah.manage:templates/directive-view.pt')

    def __init__(self, request):
        self.request = request

    def getInfo(self, action):
        info = action.info
        factory = action.info.context

        if inspect.isclass(factory):
            isclass = True
            name,context,template,route,layout,permission = action.args
        else:
            isclass = False
            factory,name,context,template,route,layout,permission = action.args

        if route:
            if name:
                view = 'view: "%s" route: "%s"'%(name, route)
            else:
                view = 'route: "%s"'%route
        else:
            view = 'view: %s'%name

        if isclass:
            factoryInfo = '%s.%s'%(factory.__module__, factory.__name__)
        else:
            factoryInfo = '%s.%s'%(info.module.__name__, factory.__name__)

        if template:
            template = template.spec
        else:
            template = ''

        return locals()

    def renderActions(self, *actions):
        return self.actions(
            getInfo = self.getInfo,
            actions = actions,
            request = self.request)
