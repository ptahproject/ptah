""" martian directives """
import martian
from martian.directive import Directive, CLASS, ONCE, ONCE_NOBASE, ONCE_IFACE

from memphis.config.directives import getInfo


class pagelet(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    def factory(self, pageletType, context=None, template=None, layer=None):
        return pageletType, context, template, layer, getInfo()


class pageletType(Directive):
    scope = CLASS
    store = ONCE_IFACE

    def factory(self, name, context=None):
        return name, context, getInfo()


class zopeView(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    def factory(self, name, context=None, template=None, layer=None, 
                layout='', permission='', default=False, decorator=None):
        return name, context, layer, template, \
            layout, permission, default, decorator, getInfo()


class pyramidView(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    def factory(self, name, context=None, template=None,
                layer=None, layout='', permission='', default=False):
        return name, context, layer, template, \
            layout, permission, default, getInfo()


class layout(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    def factory(self, name='', context=None, view=None, parent='',
                layer=None, skipParent=False, **kwargs):
        return name, context, view, parent, layer, skipParent, kwargs, getInfo()
