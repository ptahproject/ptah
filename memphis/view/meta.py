""" martian grokkers """
import martian
from zope import interface
from zope.interface.interface import InterfaceClass

from memphis import config
from memphis.view import pageletType, Pagelet, pagelet, layout
from memphis.view.pagelet import registerPageletImpl
from memphis.view.pagelet import registerPageletTypeImpl
from memphis.view.layout import Layout, registerLayoutImpl

_marker = object()

typesExecuted = []
pageletsExecuted = []
layoutsExecuted = []


@config.cleanup
def cleanUp():
    global typesExecuted, viewsExecuted, pageletsExecuted, layoutsExecutes
    typesExecuted = []
    pageletsExecuted = []
    layoutsExecutes = []


class PageletTypeGrokker(martian.InstanceGrokker):
    martian.component(InterfaceClass)
    martian.directive(pageletType)

    def grok(self, name, interface, configContext=config.UNSET, **kw):
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


class PageletGrokker(martian.ClassGrokker):
    martian.component(Pagelet)
    martian.directive(pagelet)

    def execute(self, klass, configContext=config.UNSET, **kw):
        if klass in pageletsExecuted:
            return False
        pageletsExecuted.append(klass)

        value = pagelet.bind(default=_marker).get(klass)
        if value is _marker:
            return False

        pageletType, context, template, layer, info = value
        if layer is None:
            layer = interface.Interface

        config.addAction(
            configContext,
            discriminator = ('memphis.view:pagelet',pageletType,context,layer),
            callable = registerPageletImpl,
            args = (pageletType, context, klass, template, layer),
            order = (config.moduleNum(klass.__module__), 300),
            info = info)
        return True


class LayoutGrokker(martian.ClassGrokker):
    martian.component(Layout)
    martian.directive(layout)

    def execute(self, klass, configContext=config.UNSET, **kw):
        if klass in layoutsExecuted:
            return False
        layoutsExecuted.append(klass)

        value = layout.bind(default=_marker).get(klass)
        if value is _marker:
            return False

        name, context, view, parent, layer, kwargs, info = value
        if layer is None:
            layer = interface.Interface

        config.addAction(
            configContext,
            discriminator = ('memphis.view:layout', name, context, view, layer),
            callable = registerLayoutImpl,
            args = (name, context, view, None, 
                    parent, klass, layer, configContext, info),
            order = (config.moduleNum(klass.__module__), 300),
            info = info,
            **kwargs)

        return True
