""" pagelet implementation """
import sys, logging
from webob.exc import HTTPNotFound

from zope import interface, component
from zope.component import queryUtility, queryMultiAdapter
from zope.interface.interface import InterfaceClass

from memphis import config
from memphis.view.formatter import format
from memphis.config.directives import getInfo
from memphis.view.interfaces import IPagelet, IPageletType

log = logging.getLogger('memphis.view')


class Pagelet(object):
    interface.implements(IPagelet)

    template = None
    _params = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        pass

    def render(self):
        kwargs = self._params or {}
        kwargs.update({'view': self,
                       'context': self.context,
                       'request': self.request,
                       'nothing': None,
                       'format': format,
                       'template': self.template})

        return self.template(**kwargs)

    def __call__(self, *args, **kw):
        self._params = self.update()
        return self.render()


class PageletType(object):
    interface.implements(IPageletType)

    def __init__(self, name, type, context):
        self.name = name
        self.type = type
        self.context = context


def renderPagelet(ptype, context, request):
    pagelet = queryMultiAdapter((context, request), ptype)
    if pagelet is None:
        raise HTTPNotFound

    try:
        return pagelet()
    except Exception, e:
        log.exception(str(e))
        raise


def registerPageletType(name, iface, context, configContext=config.UNSET):

    config.action(
        registerPageletTypeImpl,
        name, iface, context, configContext, getInfo(),
        __frame = sys._getframe(1))


def registerPageletTypeImpl(name, iface, context, 
                            configContext=config.UNSET, info=''):
    pt = PageletType(name, iface, context)

    iface.setTaggedValue('memphis.view.pageletType', pt)
    config.registerUtility(pt, IPageletType, name, configContext, info)


_registered = []

@config.cleanup
def cleanUp():
    _registered[:] = []


def registerPagelet(
    pageletType, context=None, klass=None,
    template=None, layer=interface.Interface, configContext=config.UNSET, **kw):

    frame = sys._getframe(1)

    config.action(
        registerPageletImpl,
        pageletType, context, klass,
        template, layer, configContext, getInfo(2), 
        __frame = frame,
        __discriminator = ('memphis.view:pagelet', pageletType, context, layer),
        __order = (config.moduleNum(frame.f_locals['__name__']), 300),
        **kw)


def registerPageletImpl(
    pageletType, context=None, klass=None,
    template=None, layer=interface.Interface, 
    configContext=config.UNSET, info='', **kw):

    if klass is not None and klass in _registered:
        raise ValueError("Class can be used for pagelet only once.")

    cdict = dict(kw)
    if template is not None:
        cdict['template'] = template

    # find PageletType info
    pt = pageletType.queryTaggedValue('memphis.view.pageletType', None)
    if pt is None:
        raise LookupError(
            "Can't find pagelet type: '%s'"%pageletType)

    if context is None:
        requires = [pt.context, layer]
    else:
        requires = [context, layer]

    # Build a new class
    if klass is not None and issubclass(klass, Pagelet):
        _registered.append(klass)
        pagelet_class = klass
        for attr, value in cdict.items():
            setattr(pagelet_class, attr, value)
    else:
        # Build a new class
        if klass is None:
            bases = (Pagelet,)
        else:
            bases = (klass, Pagelet)
            
        pagelet_class = type('Pagelet %s'%klass, bases, cdict)

    if not pt.type.implementedBy(pagelet_class):
        interface.classImplements(pagelet_class, pt.type)

    # register pagelet
    component.getSiteManager().registerAdapter(pagelet_class, requires, pt.type)
