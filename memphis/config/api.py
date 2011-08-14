"""
Test for `registerUtility`, later registration on `config.commit`::

    >>> begin()

    >>> from zope import interface, component
    >>> from zope.component import getSiteManager
    >>> class ITest1(interface.Interface):
    ...     pass
    >>> class ITest2(interface.Interface):
    ...     pass

    >>> @interface.implementer(ITest2)
    ... def testAdapter(ob):
    ...     return ob

    >>> registerAdapter(testAdapter, (ITest1,))

    >>> class Ob(object):
    ...     def __init__(self, iface):
    ...         interface.directlyProvides(self, iface)

    >>> sm = getSiteManager()

    >>> sm.getAdapter(Ob(ITest1), ITest2)
    Traceback (most recent call last):
    ...
    ComponentLookupError: ...

    >>> commit()

    >>> sm.getAdapter(Ob(ITest1), ITest2)
    <memphis.config.TESTS.Ob object at ...>

Now config context is None, so action should be executed immedietly::

    >>> registerAdapter(testAdapter, (ITest2,), ITest1)
    >>> sm.getAdapter(Ob(ITest2), ITest1)
    <memphis.config.TESTS.Ob object at ...>

Callable instance as adapter::

    >>> begin()
    >>> commit()

    >>> class Adapter(object):
    ...     component.adapts(ITest1)
    ...     interface.implements(ITest2)
    ...
    ...     def __init__(self, ob):
    ...         self.ob = ob
    ...     def __call__(self, ad):
    ...         return self.ob

    >>> adOb = Adapter(Ob(ITest2))
    >>> registerAdapter(adOb)

    >>> sm.getAdapter(Ob(ITest1), ITest2) is adOb.ob
    True

    >>> registerAdapter(Adapter)

    >>> sm.getAdapter(Ob(ITest1), ITest2)
    <memphis.config.TESTS.Adapter ...>

Test for `registerHanlder`, later registration on `config.commit`::

    >>> begin()

    >>> def testHandler(ob):
    ...     print 'test handler'

    >>> registerHandler(testHandler, (ITest1,))
    >>> s = sm.subscribers((Ob(ITest1),), None)

    >>> commit()

    >>> s = sm.subscribers((Ob(ITest1),), None)
    test handler

Registration without configuration context::

    >>> registerHandler(testHandler, (ITest2,))
    >>> s = sm.subscribers((Ob(ITest2),), None)
    test handler

loadPackage

    >>> from memphis.config import api
    >>> api.grokkerPackages = []
    >>> loadPackage('memphis.config')
    >>> api.grokkerPackages
    ['memphis.config.meta', 'memphis.config']

"""
import types
import martian
import pkg_resources
from zope import interface, component
from zope.component import getSiteManager
from zope.configuration.config import GroupingContextDecorator
from zope.configuration.config import ConfigurationMachine
from zope.configuration.xmlconfig import registerCommonDirectives


UNSET = object()
configContext = None
grokkerRegistry = martian.GrokkerRegistry()
grokkerPackages = []
grokkerPackagesExcludes = {}
cleanups = []
modulenum = {}
modulenext = 0


def getContext():
    return configContext


def begin(packages=None):
    global configContext, grokkerPackages
    if configContext is not None:
        commit()

    grokkerRegistry.clear()
    configContext = ConfigurationMachine()
    registerCommonDirectives(configContext)
    configContext.registry = getSiteManager()
    configContext.autocommit = False

    for name in packages or grokkerPackages:
        excludes = grokkerPackagesExcludes.get(name, ())

        def exclude(modname):
            if not modname.endswith('.pt'):
                if modname not in ('tests','testing','ftests') and \
                        modname not in excludes:
                    return False
            return True

        martian.grok_dotted_name(
            name, grokkerRegistry, exclude_filter=exclude,
            configContext=configContext)


def commit():
    global configContext, modulenext

    if configContext is not None:
        config = configContext
        configContext = None
        config.execute_actions()
        modulenum.clear()
        modulenext = 1


def moduleNum(name):
    global modulenext

    if name in modulenum:
        return modulenum[name]

    modulenext += 1
    modulenum[name] = modulenext
    return modulenext


def addPackage(name, excludes=()):
    if name not in grokkerPackages:
        grokkerPackages.append(name)
        if excludes:
            grokkerPackagesExcludes[name] = excludes

        if configContext is not None:
            # seems configuration system already initialized
            def exclude(modname):
                if not modname.endswith('.pt'):
                    if modname not in ('tests','testing','ftests') and \
                            modname not in excludes:
                        return False
                return True

            martian.grok_dotted_name(
                name, grokkerRegistry, exclude_filter=exclude,
                configContext=configContext)


def action(context=UNSET, discriminator=None,
           callable=None, args=(), kw={}, order=0, info=''):
    if context is None or context is UNSET:
        context = getContext()

    if context is None:
        callable(*args, **kw)
    else:
        context.action(discriminator, callable, args, kw, order, info=info)


def registerAdapter(factory, required=None, provides=None, name=u'',
                    configContext=UNSET, order=0, info=''):
    def _register():
        getSiteManager().registerAdapter(factory, required, provides, name)

    if required is None:
        required = component.adaptedBy(factory)

    if provides is None:
        if type(factory) is type:
            provides = list(interface.implementedBy(factory))[0]
        elif hasattr(factory, 'func_name'):
            provides = list(interface.implementedBy(factory))[0]
        elif isinstance(type(factory), object):
            provides = list(interface.providedBy(factory))[0]
            if required is None:
                required = factory.__class__.__component_adapts__

    if configContext is UNSET:
        configContext = getContext()

    if configContext is None:
        _register()
    else:
        action(
            configContext, ('adapter', required, provides, name),
            callable = _register, order = order, info=info)


def registerUtility(comp, provides=None, name='', 
                    configContext=UNSET, order = 0, info=''):
    def _register():
        getSiteManager().registerUtility(comp, provides, name)

    if configContext is UNSET:
        configContext = getContext()

    if configContext is None:
        _register()
    else:
        action(
            configContext, ('utility', provides, name),
            callable = _register, order = order, info=info)


def registerHandler(handler, requires=None, 
                    configContext=UNSET, order = 0, info=''):
    def _register():
        getSiteManager().registerHandler(handler, requires)

    if configContext is UNSET:
        configContext = getContext()

    if configContext is None:
        _register()
    else:
        action(configContext, None,
               callable = _register, args=(), order = order, info='')


def loadPackage(name, seen=None, first=True):
    if seen is None:
        seen = set()
    seen.add(name)

    dist = pkg_resources.get_distribution(name)

    for req in dist.requires():
        pkg = req.project_name
        if pkg in seen:
            continue
        loadPackage(pkg, seen, False)

    distmap = pkg_resources.get_entry_map(dist, 'memphis')

    ep = distmap.get('grokker')
    if ep is not None:
        addPackage(ep.module_name)

    ep = distmap.get('package')
    if ep is not None:
        addPackage(ep.module_name)

    if first:
        addPackage(name)


def loadPackages():
    seen = set()

    for dist in pkg_resources.working_set:
        pkg = dist.project_name
        if pkg in seen:
            continue

        distmap = pkg_resources.get_entry_map(dist, 'memphis')

        if 'grokker' in distmap or 'package' in distmap:
            loadPackage(pkg, seen)
        else:
            seen.add(pkg)


def notify(*event):
    getSiteManager().subscribers(event, None)


def cleanup(handler):
    registerCleanup(handler)
    return handler


def registerCleanup(handler):
    if handler not in cleanups:
        cleanups.append(handler)


def cleanUp():
    global grokkerPackages, grokkerPackagesExcludes, modulenext

    grokkerRegistry.clear()
    grokkerPackages = []
    grokkerPackagesExcludes = {}
    modulenum.clear()
    modulenext = 1

    for h in cleanups:
        h()
