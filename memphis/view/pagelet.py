""" pagelet implementation """
import sys, logging
from zope import interface
from pyramid.httpexceptions import HTTPNotFound

from memphis import config
from memphis.view.base import View
from memphis.view.customize import LayerWrapper
from memphis.view.formatter import format
from memphis.view.interfaces import IPagelet

log = logging.getLogger('memphis.view')

ptypes = {}


class Pagelet(View):
    interface.implements(IPagelet)

    template = None
    _params = None

    def render(self):
        kwargs = self._params or {}
        kwargs.update({'view': self,
                       'context': self.context,
                       'request': self.request,
                       'format': format})

        return self.template(**kwargs)

    def __call__(self, *args, **kw):
        self._params = self.update()
        return self.render()


class PageletType(object):

    def __init__(self, name, context, title, description):
        self.name = name
        self.context = context
        self.title = title
        self.description = description


def renderPagelet(ptype, context, request):
    pagelet = config.registry.queryMultiAdapter(
        (context, request), IPagelet, ptype)
    if pagelet is None:
        raise HTTPNotFound

    try:
        return pagelet()
    except Exception, e:
        log.exception(str(e))
        raise


def pageletType(name, context, title='', description=''):
    ptypes[name] = PageletType(name, context, title, description)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            pageletTypeImpl,
            (name, context, title, description),
            discriminator = ('memphis.view:pageletType', name),
            order = 1))


def pageletTypeImpl(name, context, title, description):
    ptypes[name] = PageletType(name, context, title, description)


_registered = []

@config.addCleanup
def cleanUp():
    _registered[:] = []


def registerPagelet(pt, context=None, klass=None, template=None, layer=''):
    info = config.DirectiveInfo()

    discriminator = ('memphis.view:pagelet', pt, context, layer)

    info.attach(
        config.Action(
            LayerWrapper(registerPageletImpl, discriminator),
            (klass, pt, context, template),
            discriminator = discriminator)
        )


def registerPageletImpl(klass, ptype, context, template):

    if klass is not None and klass in _registered:
        raise ValueError("Class can be used for pagelet only once.")

    cdict = {}
    if template is not None:
        cdict['template'] = template

    # find PageletType info
    if ptype not in ptypes:
        raise KeyError("Can't find pageletType %s for %s"%(ptype, klass))

    pt = ptypes[ptype]

    if context is None:
        requires = [pt.context, interface.Interface]
    else:
        requires = [context, interface.Interface]

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

    # register pagelet
    config.registry.registerAdapter(
        pagelet_class, requires, IPagelet, name = pt.name)
