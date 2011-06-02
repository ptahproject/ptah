""" martian grokkers """
import martian
from pyramid.interfaces import IRequest
from zope import interface
from zope.interface.interface import InterfaceClass

from memphis import config
from memphis.view import interfaces, pageletType, \
    View, pyramidView, Pagelet, pagelet
from memphis.view.view import registerViewImpl
from memphis.view.pagelet import registerPageletImpl
from memphis.view.pagelet import registerPageletTypeImpl

_marker = object()

typesExecuted = []
viewsExecuted = []
pageletsExecuted = []


@config.cleanup
def cleanUp():
    global typesExecuted, viewsExecuted, pageletsExecuted
    typesExecuted = []
    viewsExecuted = []
    pageletsExecuted = []


class PageletTypeGrokker(martian.InstanceGrokker):
    martian.component(InterfaceClass)
    martian.directive(pageletType)

    def grok(self, name, interface, configContext=None, **kw):
        if interface in typesExecuted:
            return False
        typesExecuted.append(interface)

        value = pageletType.bind(default=_marker).get(interface)
        if value is _marker:
            return False

        name, context, info = value

        registerPageletTypeImpl(
            name, interface, context, configContext, info)
        return True


class PyramidViewGrokker(martian.ClassGrokker):
    martian.component(View)
    martian.directive(pyramidView)

    def execute(self, klass, configContext=None, **kw):
        if klass in viewsExecuted:
            return False
        viewsExecuted.append(klass)

        value = pyramidView.bind(default=_marker).get(klass)
        if value is _marker:
            return False

        name, context, layer, template, layout, permission, info = value
        if layer is None:
            layer = IRequest

        registerViewImpl(
            name, context, klass, template, layer, layout, permission,
            configContext, info)
        return True


class PageletGrokker(martian.ClassGrokker):
    martian.component(Pagelet)
    martian.directive(pagelet)

    def execute(self, klass, configContext=None, **kw):
        if klass in pageletsExecuted:
            return False
        pageletsExecuted.append(klass)

        value = pagelet.bind(default=_marker).get(klass)
        if value is _marker:
            return False

        pageletType, context, template, layer, info = value
        if layer is None:
            layer = IRequest

        registerPageletImpl(pageletType, context, klass,
                            template, layer, configContext, info)
        return True
