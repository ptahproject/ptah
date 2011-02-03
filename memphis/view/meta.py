"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
import martian
from pyramid.interfaces import IRequest
from zope import interface
from zope.interface.interface import InterfaceClass

from memphis.view import interfaces, pagelet, pageletType, View, pyramidView

_marker = object()


typesExecuted = []


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

        pagelet.registerPageletType(
            name, interface, context, configContext, info)
        return True


class ViewGrokker(martian.ClassGrokker):
    martian.component(View)
    martian.directive(pyramidView)

    def execute(self, klass, configContext=None, **kw):
        value = pyramidView.bind(default=_marker).get(klass)
        if value is _marker:
            return False

        name, context, layer, template, layout, permission = value

        registerView(
            name, context, klass, layer, template, layout, permission,
            configContext, info)
        return True
