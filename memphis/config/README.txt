=====================
Memphis configuration
=====================

fixme: Write high level description/goals for configuration system


Each package that uses `memphis.config` should add itself to configuration
system::

    >>> import sys
    >>> from memphis import config
    >>> from zope.component import testing as catesting

    >>> config.begin()
    >>> config.addPackage('memphis.config.TESTS', excludes=['zcml'])


You can do this before config initialized or before commit. Nothing happens
if package is adding after configuration commit.


configuration:

    >>> from zope import interface, component
    >>> sm = component.getSiteManager()

    >>> class Content(object):
    ...     def __init__(self, iface):
    ...         interface.directlyProvides(self, iface)
    ...         self.iface = iface
    ...     def __str__(self):
    ...         return 'Content<%s>'%self.iface.__name__


adapter
-------

    >>> class IObject(interface.Interface):
    ...     pass

    >>> class IObject1(interface.Interface):
    ...     pass

    >>> class IAdapted(interface.Interface):
    ...     pass

    >>> class IAdapted1(interface.Interface):
    ...     pass


Registering function as adapter::

    >>> config.begin()

    >>> @config.adapter(IObject)
    ... @interface.implementer(IAdapted)
    ... def adaptObject(ob):
    ...     return Content(IAdapted)

    >>> reGrok()

    >>> print sm.queryAdapter(Content(IObject), IAdapted)
    None

    >>> config.commit()

    >>> print sm.queryAdapter(Content(IObject), IAdapted)
    Content<IAdapted>

    >>> del sys.modules[__name__].adaptObject
    >>> catesting.tearDown()


It's possible to register function as different adapter:

    >>> config.begin()

    >>> @config.adapter(IObject)
    ... @config.adapter(IObject1)
    ... @interface.implementer(IAdapted)
    ... def adaptObject(ob):
    ...     return Content(IAdapted)

    >>> reGrok()

    >>> print sm.queryAdapter(Content(IObject), IAdapted)
    None
    >>> print sm.queryAdapter(Content(IObject), IAdapted)
    None

    >>> config.commit()

    >>> print sm.queryAdapter(Content(IObject), IAdapted)
    Content<IAdapted>
    >>> print sm.queryAdapter(Content(IObject1), IAdapted)
    Content<IAdapted>

    >>> del sys.modules[__name__].adaptObject
    >>> catesting.tearDown()


Registering class as adapter::

    >>> config.begin()

    >>> class IObject2(interface.Interface):
    ...     pass

    >>> class ContentAdapter(Content):
    ...     interface.implements(IAdapted)
    ...     config.adapts(IObject2, 'test')
    ...     
    ...     def __init__(self, content):
    ...         self.content = content
    ...         self.iface = IAdapted

    >>> reGrok()

    >>> print sm.queryAdapter(Content(IObject2), IAdapted, 'test')
    None

    >>> config.commit()

    >>> print sm.queryAdapter(Content(IObject2), IAdapted, 'test')
    Content<IAdapted>

    >>> catesting.tearDown()

If configuration context is not set adapters are registered immidietly:

    >>> @config.adapter(IObject)
    ... @interface.implementer(IAdapted)
    ... def adaptObject(ob):
    ...     return Content(IAdapted)

    >>> reGrok()

    >>> print sm.queryAdapter(Content(IObject), IAdapted)
    Content<IAdapted>

    >>> catesting.tearDown()

Registering function as adapter:

    >>> config.registerAdapter(adaptObject)
    >>> print sm.queryAdapter(Content(IObject), IAdapted)
    Content<IAdapted>

    >>> catesting.tearDown()


utility
-------

    >>> config.begin()

    >>> ob = Content(IObject)
    >>> config.registerUtility(ob, IObject, 'test')

    >>> print sm.queryUtility(IObject, 'test')
    None

    >>> config.commit()

    >>> ob is sm.queryUtility(IObject, 'test')
    True

    >>> ob = Content(IObject1)
    >>> config.registerUtility(ob, IObject1, 'test1')

    >>> ob is sm.queryUtility(IObject1, 'test1')
    True

    >>> catesting.tearDown()


class as utility

    >>> config.begin()

    >>> class ContentUtility(object):
    ...     config.utility(IObject, 'test')

    >>> reGrok()

    >>> print sm.queryUtility(IObject, 'test')
    None

    >>> config.commit()

    >>> sm.queryUtility(IObject, 'test')
    <memphis.config.TESTS.ContentUtility ...>

    >>> del sys.modules[__name__].ContentUtility
    >>> catesting.tearDown()


config action
-------------

It's possible to run any function on config commit, and rerun function
each time config is reinitialized (testing support)::

    >>> def testFunc():
    ...     print "My test function"

    >>> config.begin()

    >>> _ = config.action(testFunc, discriminator=('test',), actionOrder=10)

    >>> reGrok()

    >>> config.commit()
    My test function

    >>> reGrok()
    My test function


Without `discriminator` configAction executed immidietly.

    >>> del locals()['memphis.config.directives.action']

    >>> config.begin()

    >>> def testFunc1():
    ...     print "My test1 function"

    >>> _ = config.action(testFunc1)

    >>> reGrok()
    My test1 function

    >>> config.commit()
    My test function

    reGrok()
    My test function
    My test1 function
