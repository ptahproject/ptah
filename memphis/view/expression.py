"""

$Id: expression.py 11635 2011-01-18 07:03:08Z fafhrd91 $
"""
import logging
from chameleon.core import types
from chameleon.zpt import expressions
from chameleon.zpt.interfaces import IExpressionTranslator

from zope import component
from zope.component import getUtility, queryUtility, queryMultiAdapter

from memphis import config
from memphis.view.interfaces import IPageletType

log = logging.getLogger('memphis.view')


class PageletTraverser(object):

    def __call__(self, name, context, request):
        try:
            pt = getUtility(IPageletType, name)
            pagelet = queryMultiAdapter((context, request), pt.type)
            if pagelet is not None:
                return pagelet()
        except Exception, e:
            log.exception(str(e))

        return u''


class PageletTranslator(expressions.ExpressionTranslator):
    config.utility(IExpressionTranslator, 'pagelet')

    symbol = '_get_memphis_pagelet'
    pagelet_traverser = PageletTraverser()

    def translate(self, string, escape=None):
        if '/' in string:
            name, ptname = string.split('/', 1)
        else:
            name = 'context'
            ptname = string

        pt = queryUtility(IPageletType, ptname)
        if pt is None:
            log.warning("Can't find pagelet type: %s"%string)
            return types.value("")

        value = types.value("%s('%s', %s, request)" % \
                                (self.symbol, ptname, name))
        value.symbol_mapping[self.symbol] = self.pagelet_traverser
        return value
