""" base view class with access to various api's """
import logging
from zope import interface
from ptah.formatter import format
from ptah.view.resources import static_url
from ptah.view.message import add_message, render_messages
from ptah.view.library import include, render_includes
from ptah.view.interfaces import ISnippet, IPtahView

log = logging.getLogger('ptah.view')


class View(object):
    interface.implements(IPtahView)

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
            kwargs = {'view': self,
                      'context': self.context,
                      'request': self.request}
            if type(params) is dict:
                kwargs.update(params)
            return self.template(**kwargs)

        return u''

    def include(self, name):
        include(self.request, name)

    def render_includes(self):
        return render_includes(self.request)

    def message(self, msg, type='info'):
        return add_message(self.request, msg, type)

    def render_messages(self):
        return render_messages(self.request)

    def static_url(self, name, path=''):
        return static_url(self.request, name, path)

    def snippet(self, stype, context=None):
        if context is None:
            context = self.context

        request = self.request

        try:
            snippet = request.registry.queryMultiAdapter(
                (context, request), ISnippet, stype)
            if snippet is not None:
                return snippet()
        except Exception, e:
            log.exception(str(e))

        return u''
