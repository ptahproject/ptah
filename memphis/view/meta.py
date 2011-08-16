""" martian grokkers """
import martian
from zope import interface
from zope.interface.interface import InterfaceClass

from pyramid.interfaces import IRequest

from memphis import config
from memphis.view import pageletType, Pagelet, pagelet, layout, pyramidView
from memphis.view.view import View, registerViewImpl
from memphis.view.layout import Layout, registerLayoutImpl
from memphis.view.pagelet import registerPageletImpl, registerPageletTypeImpl

_marker = object()


class PageletTypeGrokker(martian.InstanceGrokker):
    martian.component(InterfaceClass)
    martian.directive(pageletType)

    def grok(self, name, interface, configContext=config.UNSET, **kw):
        if interface in _typesExecuted:
            return False
        _typesExecuted.append(interface)

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
        if klass in _pageletsExecuted:
            return False
        _pageletsExecuted.append(klass)

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
        if klass in _layoutsExecuted:
            return False
        _layoutsExecuted.append(klass)

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
                    parent, klass, layer, config.UNSET, info),
            order = (config.moduleNum(klass.__module__), 300),
            info = info,
            **kwargs)

        return True


class PyramidViewGrokker(martian.ClassGrokker):
    martian.component(View)
    martian.directive(pyramidView)

    def execute(self, klass, configContext=config.UNSET, **kw):
        if klass in _viewsExecuted:
            return False
        _viewsExecuted.append(klass)

        value = pyramidView.bind(default=_marker).get(klass)
        if value is _marker:
            return False

        name, context, layer, template, \
            layout, permission, default, decorator, info = value

        if layer is None:
            layer = IRequest

        config.addAction(
            configContext, 
            discriminator = (
                'memphis.view:pyramidView', name, context, layer), 
            callable = registerViewImpl, 
            args = (name, klass, context, template, layer, layout, permission,
                    default, decorator, config.UNSET, info),
            info = info)

        return True


_typesExecuted = []
_pageletsExecuted = []
_layoutsExecuted = []
_viewsExecuted = []

@config.cleanup
def cleanUp():
    _pageletsExecuted[:] = []
    _layoutsExecuted[:] = []
    _typesExecuted[:] = []
    _viewsExecuted[:] = []

