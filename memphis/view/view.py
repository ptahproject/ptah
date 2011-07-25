""" view implementation """
import json, sys
from zope import interface
from webob import Response
from webob.exc import HTTPException

from memphis.view.compat import IView
from memphis.view.layout import queryLayout
from memphis.view.interfaces import IRenderer


class View(object):
    interface.implements(IView)

    __name__ = ''
    template = None
    layout = ''

    content_type = 'text/html'
    response_status = 200
    
    _params = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context
        self.response_headers = {}

    def update(self):
        pass

    def render(self):
        kwargs = self._params or {}
        kwargs.update({'view': self,
                       'context': self.context,
                       'request': self.request,
                       'nothing': None})

        return self.template(**kwargs)

    def __call__(self, *args, **kw):
        try:
            self._params = self.update()

            if self.layout is None:
                res = self.render()
            else:
                layout = queryLayout(
                    self, self.request, self.__parent__, self.layout)
                if layout is None:
                    res = self.render()
                else:
                    res = layout()

            return Response(body = res, 
                            status = self.response_status,
                            headerlist = self.response_headers.items(),
                            content_type = self.content_type)
        except HTTPException, response:
            return response


def subpathWrapper(view):
    if not getattr(view, '__subpath_traverse__', None):
        return

    call = view.__call__
    subpaths = view.__subpath_traverse__

    def wrapper(self, *args, **kw):
        request = self.request
        if request.subpath:
            item = request.subpath[0]
            if item in subpaths:
                meth = subpaths[item]
                request.subpath = tuple(request.subpath[1:])
                try:
                    res = meth(self)
                    if isinstance(res, Response):
                        return res
                    return Response(body = res,
                                    status = self.response_status,
                                    headerlist = self.response_headers.items(),
                                    content_type = self.content_type)
                except HTTPException, response:
                    return response

        return call(self, *args, **kw)

    view.__call__ = wrapper


class subpath:

    def __init__(self, name='', 
                 renderer=None, template=None, content_type=None, 
                 decorator=None, updateView=False):
        self.name = name
        self.renderer = renderer
        self.template = template
        self.decorator = decorator
        self.updateView = updateView

        if content_type is None and IRenderer.providedBy(renderer):
            content_type = renderer.content_type

        if content_type is None:
            content_type = 'text/html'

        self.content_type = content_type

    def __call__(self, ob):
        frame = sys._getframe(1)
        if '__module__' not in frame.f_locals:
            del frame
            raise ValueError(
                "Can apply 'subpath' decorator only to class methods")

        subpaths = frame.f_locals.get('__subpath_traverse__', None)
        if subpaths is None:
            subpaths = {}
            frame.f_locals['__subpath_traverse__'] = subpaths

        del frame

        if self.decorator:
            pathMeth = decorator(ob)
        else:
            pathMeth = ob

        updateView = self.updateView
        content_type = self.content_type

        if self.renderer:
            def renderSubpath(viewInst):
                viewInst.content_type = content_type
                if updateView:
                    viewInst.update()

                return self.renderer(pathMeth(viewInst))
        elif self.template:
            def renderSubpath(viewInst):
                kwargs = {'view': viewInst,
                          'context': viewInst.context,
                          'request': viewInst.request,
                          'nothing': None}

                viewInst.content_type = content_type
                if updateView:
                    params = viewInst.update()
                    if params is not None:
                        kwargs.update(params)

                kwargs.update(pathMeth(viewInst))
                return self.template(**kwargs)
        else:
            def renderSubpath(viewInst):
                viewInst.content_type = content_type
                if updateView:
                    viewInst.update()

                return pathMeth(viewInst)

        if self.name:
            subpaths[self.name] = renderSubpath
        else:
            subpaths[ob.__name__] = renderSubpath

        return ob


class JSONRenderer(object):
    interface.implements(IRenderer)

    content_type = 'text/json'

    def __call__(self, result, dumps=json.dumps):
        return dumps(result)


json = JSONRenderer()
