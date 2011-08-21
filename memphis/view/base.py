""" base view class with access to various api's """
import logging
from zope import interface
from zope.component import getUtility, getSiteManager
from memphis.view.formatter import format
from memphis.view.resources import static, static_url
from memphis.view.message import addMessage, renderMessages
from memphis.view.library import library, include, renderIncludes
from memphis.view.interfaces import IPageletType, IMemphisView

log = logging.getLogger('memphis.view')


class View(object):
    interface.implements(IMemphisView)

    __name__ = ''
    __parent__ = None

    format = format

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

    def update(self):
        pass

    def render(self):
        return u''

    def include(self, name):
        include(name, self.request)

    def renderIncludes(self):
        return renderIncludes(self.request)

    def message(self, msg, type='info'):
        return addMessage(self.request, msg, type)

    def renderMessages(self):
        return renderMessages(self.request)

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


static('bootstrap', 'memphis.view:bootstrap')

library(
    'lesscss',
    path="less-1.1.3.min.js",
    resource="bootstrap",
    type="js")

library(
    'bootstrap',
    path="bootstrap-1.0.0.min.css",
    resource="bootstrap",
    type="css")

library(
    'bootstrap-less',
    path="lib/bootstrap.less",
    resource="bootstrap",
    type="css",
    extra={'rel': 'stylesheet/less'})
