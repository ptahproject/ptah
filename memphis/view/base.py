""" base view class with access to various api's """
import logging
from zope.component import getUtility
from memphis.view.formatter import format
from memphis.view.resources import static_url
from memphis.view.library import library, include, renderIncludes
from memphis.view.interfaces import IPageletType

log = logging.getLogger('memphis.view')


class Base(object):

    request = None
    format = format

    def include(self, name):
        include(name, self.request)

    def renderIncludes(self):
        return renderIncludes(self.request)

    def static_url(self, name, path=''):
        return static_url(name, path, self.request)
    
    def pagelet(self, context, ptype):
        if isinstance(ptype, basestring):
            try:
                pt = getUtility(IPageletType, ptype)
            except:
                log.warning("Can't find pagelet type: %s"%ptype)
                return u''
        else:
            pt = ptype.getTaggedValue('memphis.view.pageletType')

        try:
            pagelet = queryMultiAdapter((context, self.request), pt.type)
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
