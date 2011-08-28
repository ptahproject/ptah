""" introspect module """
import ptah
import pkg_resources, inspect, os, sys
from zope import interface
from memphis import config, view
from memphis.config import directives
from memphis.config.api import exclude, loadPackages

from zope import interface
from interfaces import IIntrospectModule, IPackage


class IntrospectModule(ptah.PtahModule):
    """ Introspection various aspects of memphis & ptah. """

    config.utility(name='introspect')
    interface.implementsOnly(IIntrospectModule)

    name = 'introspect'
    title = 'Introspect'
    description = 'Introspection various aspects of memphis & ptah.'

    packages = loadPackages()
    packages.sort()
    packages = [pkg_resources.get_distribution(pkg) for pkg in packages]
    packagesDict = dict((p.project_name, p) for p in packages)

    def __getitem__(self, key):
        return Package(self.packagesDict[key], self, self.request)


class Package(object):
    interface.implements(IPackage)

    def __init__(self, pkg, mod, request):
        self.__name__ = pkg.project_name
        self.__parent__ = mod

        self.pkg = pkg
        self.request = request

    def actions(self):
        actions = directives.scan(self.pkg.project_name, set(), exclude)

        info = {}

        for action in actions:
            d = action.discriminator[0]
            d_data = info.setdefault(d, {})
            mod_data = d_data.setdefault(action.info.module.__name__, [])
            mod_data.append(action)

        return info


class MainView(view.View):
    view.pyramidView(
        'index.html', IIntrospectModule,
        route = 'ptah-manage', default='True',
        template = view.template(
            'ptah.modules:templates/introspect.pt', nolayer=True))

    def update(self):
        self.packages = self.context.packages


def lineno(ob):
    if ob is not None:
        return inspect.getsourcelines(ob)[-1]


def viewDirective(
    action, request,
    lineno = lineno,
    renderer = view.template(
        'ptah.modules:templates/directive-view.pt', nolayer=True)):
    info = action.info
    factory = action.info.context

    if inspect.isclass(factory):
        isclass = True
        name, context, template, route, layout, \
            permission, default, decorator, layer, discriminator = action.args
    else:
        isclass = False
        factory, name, context, template, route, layout, permission, \
            default, decorator, layer, discriminator = action.args

    if route:
        if name:
            view = '"%s" route: "%s"'%(name, route)
        else:
            view = 'route: "%s"'%route
    else:
        view = '"%s"'%name

    if isclass:
        factoryInfo = '%s.%s'%(factory.__module__, factory.__name__)
    else:
        factoryInfo = '%s.%s'%(info.module.__name__, factory.__name__)

    if template:
        template = template.spec
    else:
        template = ''

    return renderer(**locals())


def routeDirective(
    action, request,
    lineno = lineno,
    template = view.template(
        'ptah.modules:templates/directive-route.pt', nolayer=True)):

    name, pattern, factory = action.args[:3]

    if not factory:
        factory = 'DefaultRootFactory'

    return template(**locals())


def utilityDirective(
    action, request,
    lineno = lineno,
    template=view.template(
        'ptah.modules:templates/directive-utility.pt',nolayer=True)):

    context = action.info.context
    iface, name = action.args[:2]

    if iface is None:
        provided = list(interface.implementedBy(context))
        if len(provided):
            iface = provided[0]

    return template(**locals())


def adapterDirective(
    action, request,
    lineno = lineno,
    template=view.template(
        'ptah.modules:templates/directive-adapter.pt',nolayer=True)):

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

    return template(**locals())


def handlerDirective(
    action, request,
    lineno = lineno,
    template=view.template(
        'ptah.modules:templates/directive-handler.pt',nolayer=True)):

    factory, ifaces = action.args[1:]
    factoryInfo = '%s.%s'%(action.info.module.__name__, factory.__name__)

    if len(action.args[2]) > 1:
        obj = action.args[2][0]
        event = directives.events[action.args[2][-1]]
    else:
        obj = None
        event = directives.events[action.args[2][0]]

    return template(**locals())


def eventDirective(
    action, request,
    lineno = lineno,
    template=view.template(
        'ptah.modules:templates/directive-event.pt',nolayer=True)):

    event = directives.events[action.info.context]

    return template(**locals())


def pageletTypeDirective(
    action, request,
    lineno = lineno,
    template=view.template(
        'ptah.modules:templates/directive-ptype.pt',nolayer=True)):

    name = action.args[0]
    ptype = sys.modules['memphis.view.pagelet'].ptypes[name]

    return template(**locals())


renderers = {
    'memphis.view:view': viewDirective,
    'memphis.view:route': routeDirective,
    'memphis.view:pageletType': pageletTypeDirective,
    'memphis.config:utility': utilityDirective,
    'memphis.config:adapter': adapterDirective,
    'memphis.config:handler': handlerDirective,
    'memphis.config:event': eventDirective,
    }

types = {
    'memphis.view:view': ('View', 'Pyramid views'),
    'memphis.view:route': ('Route', 'Pyramid routes'),
    'memphis.view:layout': ('Layout', 'Memphis layouts'),
    'memphis.view:pagelet': ('Pagelet', 'Memphis pagelets'),
    'memphis.view:pageletType': ('Pagelet Type', 'Memphis pagelet types'),
    'memphis.config:event': ('Events', 'event declarations'),
    'memphis.config:utility': ('Utility', 'zca utility registrations'),
    'memphis.config:adapter': ('Adapters','zca adapter registrations'),
    'memphis.config:handler': ('Event listeners',
                               'zca event handler registrations'),
    }


class PackageView(view.View):
    view.pyramidView(
        'index.html', IPackage,
        route = 'ptah-manage', default='True',
        template = view.template(
            'ptah.modules:templates/introspect-pkg.pt', nolayer=True))

    renderers = renderers
    types = types

    def update(self):
        self.data = self.context.actions()


class EventsView(view.View):
    view.pyramidView(
        'events.html', IIntrospectModule,
        route = 'ptah-manage',
        template = view.template(
            'ptah.modules:templates/introspect-events.pt', nolayer=True))

    events = None
    actions = None

    def lineno(self, ob):
        return inspect.getsourcelines(ob)[-1]

    def update(self):
        ev = self.request.params.get('ev')
        self.event = event = directives.events.get(ev)

        if event is None:
            events = []
            for n, ev in directives.events.items():
                if isinstance(n, basestring):
                    events.append((ev.title, ev))

            events.sort()
            self.events = [ev for _t, ev in events]
        else:
            pkgs = loadPackages()
            evinst = event.instance

            seen = set()
            actions = []
            for pkg in pkgs:
                for action in directives.scan(pkg, seen, exclude):
                    if action.discriminator[0] == 'memphis.config:handler':
                        required = action.args[2]
                        if len(required) == 2 and required[1] == evinst:
                            actions.append(action)
                        elif required[0] == evinst:
                            actions.append(action)

            self.actions = actions


class SourceView(view.View):
    view.pyramidView(
        'source.html', IIntrospectModule,
        route = 'ptah-manage',
        template = view.template(
            'ptah.modules:templates/introspect-source.pt', nolayer=True))

    source = None
    format = None

    def update(self):
        name = self.request.params.get('pkg')

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

                def format(code, highlight=highlight,
                           lexer = PythonLexer()):
                    return highlight(code, lexer, html)
                self.format = format

            self.source = self.format(source)
