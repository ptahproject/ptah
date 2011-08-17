""" pagelet implementation """
import sys, logging
from webob.exc import HTTPNotFound

from zope import interface
from zope.component import getSiteManager

from memphis import config
from memphis.view.base import View
from memphis.view.formatter import format
from memphis.view.interfaces import IPagelet, IPageletType

log = logging.getLogger('memphis.view')


class Pagelet(View):
    interface.implements(IPagelet)

    template = None
    _params = None

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
    pagelet = getSiteManager().queryMultiAdapter((context, request), ptype)
    if pagelet is None:
        raise HTTPNotFound

    try:
        return pagelet()
    except Exception, e:
        log.exception(str(e))
        raise


def registerPageletType(name, iface, context):
    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            registerPageletTypeImpl,
            (iface, name, context),
            discriminator = ('memphis.view:pageletType', name, iface)))


def registerPageletTypeImpl(iface, name, context):
    pt = PageletType(name, iface, context)

    iface.setTaggedValue('memphis.view.pageletType', pt)
    getSiteManager().registerUtility(pt, IPageletType, name)


_registered = []

@config.addCleanup
def cleanUp():
    _registered[:] = []


def registerPagelet(
    pageletType, context=None, 
    klass=None, template=None, layer=interface.Interface):

    info = config.DirectiveInfo()

    info.attach(
        config.Action(
            registerPageletImpl,
            (klass, pageletType, context, template, layer), 
            discriminator = ('memphis.view:pagelet',pageletType,context,layer)))


def registerPageletImpl(klass, pageletType, context, template, layer):
    if klass is not None and klass in _registered:
        raise ValueError("Class can be used for pagelet only once.")

    cdict = {}
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
    getSiteManager().registerAdapter(pagelet_class, requires, pt.type)
