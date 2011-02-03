"""

$Id: pagelet.py 11636 2011-01-18 08:14:44Z fafhrd91 $
"""
import pyramid
from pyramid.interfaces import IRequest
from pyramid.exceptions import NotFound

from zope import interface, component
from zope.component import queryUtility, queryMultiAdapter
from zope.interface.interface import InterfaceClass
from zope.configuration.exceptions import ConfigurationError

from memphis import config
from memphis.view.interfaces import IPagelet, IPageletType


class Pagelet(object):
    interface.implements(IPagelet)

    template = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        pass

    def render(self):
        kwargs = {'view': self,
                  'context': self.context,
                  'request': self.request,
                  'nothing': None,
                  'template': self.template}

        return self.template(**kwargs)

    def __call__(self, *args, **kw):
        self.update()
        return self.render()


class PageletType(object):
    interface.implements(IPageletType)

    def __init__(self, name, type, context):
        self.name = name
        self.type = type
        self.context = context


def renderPagelet(ptype, context, request):
    if isinstance(ptype, InterfaceClass):
        pt = ptype.queryTaggedValue('memphis.view.pageletType', None)
    else:
        pt = queryUtility(IPageletType, ptype)

    if pt is None:
        raise NotFound

    pagelet = queryMultiAdapter((context, request), pt.type)
    if pagelet is None:
        raise NotFound

    return pagelet()


def registerPageletType(name, iface, context, configContext=None, info=''):
    pt = PageletType(name, iface, context)

    iface.setTaggedValue('memphis.view.pageletType', pt)
    config.registerUtility(pt, IPageletType, name, configContext, info)


def registerPagelet(
    pageletType, context=None, klass=None,
    layer=IRequest, template=None, configContext=None, **kw):

    def _register(pageletType, context, klass, layer, template, kw):
        cdict = dict(kw)
        cdict['template'] = template

        # find PageletType info
        pt = pageletType.queryTaggedValue('memphis.view.pageletType', None)
        if pt is None:
            raise ConfigurationError("Can't find pagelet type: '%s'"%pageletType)

        if context is None:
            requires = [pt.context, layer]
        else:
            requires = [context, layer]

        # Build a new class
        if klass is None:
            klass = Pagelet

        if issubclass(klass, Pagelet):
            bases = (klass,)
        else:
            bases = (klass, Pagelet)

        pagelet_class = type('Pagelet %s'%klass, bases, cdict)

        if not pt.type.implementedBy(pagelet_class):
            interface.classImplements(pagelet_class, pt.type)

        # register pagelet
        component.getSiteManager().registerAdapter(
            pagelet_class, requires, pt.type)

    config.addAction(
        configContext,
        ('memphis.view:registerPagelet', pageletType, context, layer),
        callable = _register,
        args = (pageletType, context, klass, layer, template, kw))
