""" view implementation """
from zope import interface
from webob import Response
from webob.exc import HTTPException

from memphis.view.compat import IView
from memphis.view.layout import queryLayout


class View(object):
    interface.implements(IView)

    __name__ = ''
    template = None
    layoutname = ''
    content_type = 'text/html'
    
    _params = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

    def update(self):
        pass

    def render(self):
        kwargs = self._params or {}
        kwargs.update({'view': self,
                       'context': self.context,
                       'request': self.request,
                       'template': self.template,
                       'nothing': None})

        return self.template(**kwargs)

    def __call__(self, *args, **kw):
        try:
            self._params = self.update()

            layout = queryLayout(
                self, self.request, self.__parent__, self.layoutname)
            if layout is None:
                res = self.render()
            else:
                res = layout()

            return Response(body=res, status=200,
                            content_type = self.content_type)
        except HTTPException, response:
            return response
