""" chameleon tales expression """
import logging
import ast
from chameleon import astutil
from chameleon.codegen import template
from chameleon.astutil import Symbol
from chameleon.astutil import Static
from chameleon.zpt.template import PageTemplate
from chameleon.zpt.template import PageTemplateFile

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


class PageletExpr(object):

    traverser = Static(
        template("cls()", cls=Symbol(PageletTraverser), mode="eval")
        )

    def __init__(self, expression):
        if '/' in expression:
            name, ptname = expression.split('/', 1)
        else:
            name = 'context'
            ptname = expression
        self.name, self.ptname = name, ptname

    def __call__(self, target, engine):
        pt = queryUtility(IPageletType, self.ptname)
        if pt is None:
            log.warning("Can't find pagelet type: %s"%self.ptname)
            return [ast.Assign([target], ast.Str(''))]

        return template(
            "target = traverse(name, context, request)",
            target=target,
            traverse=self.traverser,
            name=ast.Str(self.ptname),
            context=astutil.load(self.name)
            )


PageTemplate.expression_types['pagelet'] = PageletExpr
PageTemplateFile.expression_types['pagelet'] = PageletExpr