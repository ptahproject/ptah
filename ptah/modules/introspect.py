""" introspect module """
import ptah
import pkg_resources, inspect
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


def viewDirective(
    action, request,
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
    template = view.template(
        'ptah.modules:templates/directive-route.pt', nolayer=True)):

    name, pattern, factory = action.args[:3]

    if not factory:
        factory = 'DefaultRootFactory'

    return template(**locals())


def utilityDirective(
    action, request,
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
    template=view.template(
        'ptah.modules:templates/directive-handler.pt',nolayer=True)):

    factory, ifaces = action.args[1:]
    factoryInfo = '%s.%s'%(action.info.module.__name__, factory.__name__)

    return template(**locals())


renderers = {
    'memphis.view:view': viewDirective,
    'memphis.view:route': routeDirective,
    'memphis.config:utility': utilityDirective,
    'memphis.config:adapter': adapterDirective,
    'memphis.config:handler': handlerDirective,
    }

types = {
    'memphis.view:view': ('View', 'Pyramid views'),
    'memphis.view:route': ('Route', 'Pyramid routes'),
    'memphis.view:layout': ('Layout', 'Memphis layouts'),
    'memphis.view:pagelet': ('Pagelet', 'Memphis pagelets'),
    'memphis.view:pageletType': ('Pagelet Type', 'Memphis pagelet types'),
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
