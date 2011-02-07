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
    ['memphis.config']

$Id: api.py 11802 2011-01-31 06:25:41Z fafhrd91 $
"""
import types
import martian
import pkg_resources
from zope import interface, component
from zope.component import getSiteManager
from zope.configuration.config import GroupingContextDecorator
from zope.configuration.config import ConfigurationMachine
from zope.configuration.xmlconfig import registerCommonDirectives


configContext = None
grokkerRegistry = martian.GrokkerRegistry()
grokkerPackages = []
grokkerPackagesExcludes = {}
cleanups = []


def getContext():
    return configContext


def begin(packages=None):
    global configContext

    for h in cleanups:
        h()

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
    global configContext

    if configContext is not None:
        configContext.execute_actions()
        configContext = None


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


def action(context=None, discriminator=None,
           callable=None, args=(), kw={}, order=0, info=''):
    if context is None:
        context = getContext()

    if context is None:
        callable(*args, **kw)
    else:
        context.info = info
        context.action(discriminator, callable, args, kw, order)


def registerAdapter(factory, required=None, provides=None, name=u'',
                    configContext=None, info=''):
    def _register(*args, **kw):
        getSiteManager().registerAdapter(*args, **kw)

    if configContext is None:
        configContext = getContext()

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

    if configContext is None:
        _register(factory, required, provides, name)
    else:
        action(
            configContext, ('adapter', required, provides, name),
            callable = _register,
            args=(factory, required, provides, name), info=info)


def registerUtility(comp, provides=None, name='', configContext=None, info=''):
    def _register(*args, **kw):
        getSiteManager().registerUtility(*args, **kw)

    if configContext is None:
        configContext = getContext()

    if configContext is None:
        _register(comp, provides, name=name)
    else:
        action(
            configContext, ('utility', provides, name),
            callable = _register,
            args=(comp, provides, name), info=info)


def registerHandler(handler, requires=None, configContext=None, info=''):
    def _register(*args, **kw):
        getSiteManager().registerHandler(*args, **kw)

    if configContext is None:
        configContext = getContext()

    if configContext is None:
        _register(handler, requires)
    else:
        action(configContext, None,
               callable = _register, args=(handler, requires), info='')


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

    ep = pkg_resources.get_entry_map(dist, 'memphis').get('include')
    if ep is not None:
        addPackage(ep.module_name)

    if first:
        addPackage(name)


def cleanup(handler):
    registerCleanup(handler)
    return handler


def registerCleanup(handler):
    if handler not in cleanups:
        cleanups.append(handler)


def cleanUp():
    global grokkerPackages, grokkerPackagesExcludes

    grokkerRegistry.clear()
    grokkerPackages = []
    grokkerPackagesExcludes = {}

    for h in cleanups:
        h()
