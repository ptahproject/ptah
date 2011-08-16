""" martian directives """
import sys
from pyramid.interfaces import IRequest

import martian
from martian.error import GrokImportError
from martian.directive import Directive, CLASS, MODULE, ONCE_NOBASE, ONCE_IFACE

from memphis import config


class pagelet(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    def factory(self, pageletType, context=None, template=None, layer=None):
        return pageletType, context, template, layer, config.getInfo()


class pageletType(Directive):
    scope = CLASS
    store = ONCE_IFACE

    def factory(self, name, context=None):
        return name, context, config.getInfo()


class pyramidView(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    deco = False

    def __init__(self, *args, **kw):
        self.name = self.__class__.__name__

        frame = kw.get('frame')
        if frame is not None:
            del kw['frame']
            self.frame = frame
        else:
            self.frame = frame = sys._getframe(1)

        self.check_factory_signature(*args, **kw)

        if not self.scope.check(frame):
            if MODULE.check(frame):
                self.deco = True
                self.value = self.factory(*args, **kw)
                return

            raise GrokImportError("The '%s' directive can only be used on "
                                  "%s level." %
                                  (self.name, self.scope.description))

        self.store.set(frame.f_locals, self, self.factory(*args, **kw))

    def __call__(self, factory):
        if self.deco:
            from memphis.view.view import registerViewImpl

            name, context, layer, template, \
                layout, permission, default, decorator, info = self.value
            if layer is None:
                layer = IRequest

            config.action(
                registerViewImpl,
                name, factory, context, template,
                layer, layout, permission, default, decorator, 
                config.UNSET, info,
                __info = info,
                __frame = self.frame,
                __discriminator = ('memphis.view:view', name, context, layer))

    def factory(self, name, context=None, template=None, layer=None, 
                layout='', permission='__no_permission_required__',
                default=False, decorator=None):
        return name, context, layer, template, \
            layout, permission, default, decorator, config.getInfo()


class layout(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    def factory(self, name='', context=None, 
                view=None, parent='', layer=None, **kw):
        return name, context, view, parent, layer, kw, config.getInfo()
