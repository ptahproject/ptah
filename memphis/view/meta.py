"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
import martian
from pyramid.interfaces import IRequest
from zope import interface
from zope.interface.interface import InterfaceClass

from memphis.view import interfaces, pageletType, \
    View, pyramidView, registerView, \
    Pagelet, pagelet, registerPagelet, registerPageletType

_marker = object()

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

        registerPageletType(
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

        registerView(
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

        registerPagelet(pageletType, context, klass, 
                        template, layer, configContext, info)
        return True
