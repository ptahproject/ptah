"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
import martian
from martian.directive import Directive, CLASS, ONCE, ONCE_NOBASE, ONCE_IFACE

from memphis.config.directives import getInfo


class pageletType(Directive):
    scope = CLASS
    store = ONCE_IFACE

    def factory(self, name, context=None):
        return name, context, getInfo()


class pyramidView(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    def factory(self, name, context=None, template=None, 
                layer=None, layout='', permission=''):
        return name, context, layer, template, layout, permission
