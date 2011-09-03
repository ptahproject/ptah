""" base view class with access to various api's """
import logging
from zope import interface
from zope.component import getUtility, getSiteManager
from memphis.view.formatter import format
from memphis.view.resources import static, static_url
from memphis.view.message import addMessage, renderMessages
from memphis.view.library import library, include, renderIncludes
from memphis.view.interfaces import IPagelet, IMemphisView, INavigationRoot

log = logging.getLogger('memphis.view')


class DefaultRoot(object):
    interface.implements(INavigationRoot)

    __name__ = None
    __parent__ = None

    def __init__(self, request=None):
        self.request = request


class View(object):
    interface.implements(IMemphisView)

    __name__ = ''
    __parent__ = None

    format = format
    template = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

    def update(self):
        return {}

    def render(self):
        params = self.update()
        if self.template is not None:
            return self.template(**params)

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

        if context is None:
            context = self.context

        try:
            pagelet = sm.queryMultiAdapter(
                (context, self.request), IPagelet, ptype)
            if pagelet is not None:
                return pagelet()
        except Exception, e:
            log.exception(str(e))

        return u''


library(
    'jquery',
    path="https://ajax.googleapis.com/ajax/libs/jquery/1.6.3/jquery.js",
    type="js")

library(
    'jquery-ui',
    path="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.js",
    type="js",
    require="jquery")

library(
    'jquery-ui',
    path="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/ui-lightness/jquery-ui.css",
    type='css')


static('bootstrap', 'memphis.view:bootstrap')

library(
    'lesscss',
    path="less-1.1.3.min.js",
    resource="bootstrap",
    type="js")

library(
    'bootstrap',
    path="bootstrap-1.2.0.min.css",
    resource="bootstrap",
    type="css")

library(
    'bootstrap-less',
    path="lib/bootstrap.less",
    resource="bootstrap",
    type="css",
    extra={'rel': 'stylesheet/less'})
