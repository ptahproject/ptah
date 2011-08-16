""" base view class with access to various api's """
import logging
from zope.component import getUtility, getSiteManager
from memphis.view.formatter import format
from memphis.view.resources import static_url
from memphis.view.message import renderMessages
from memphis.view.library import library, include, renderIncludes
from memphis.view.interfaces import IPageletType

log = logging.getLogger('memphis.view')


class BaseMixin(object):

    request = None
    context = None
    format = format

    def include(self, name):
        include(name, self.request)

    def renderIncludes(self):
        return renderIncludes(self.request)

    def static_url(self, name, path=''):
        return static_url(name, path, self.request)
    
    def pagelet(self, ptype, context=None):
        sm = getSiteManager()

        if isinstance(ptype, basestring):
            try:
                pt = sm.getUtility(IPageletType, ptype)
            except:
                log.warning("Can't find pagelet type: %s"%ptype)
                return u''
        else:
            pt = ptype.getTaggedValue('memphis.view.pageletType')

        if context is None:
            context = self.context

        try:
            pagelet = sm.queryMultiAdapter((context, self.request), pt.type)
            if pagelet is not None:
                return pagelet()
        except Exception, e:
            log.exception(str(e))

        return u''


library(
    'jquery',
    path="https://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.js",
    type="js")

library(
    'jquery-ui',
    path="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.15/jquery-ui.js",
    type="js",
    require="jquery")
