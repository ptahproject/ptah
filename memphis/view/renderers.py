""" renderers """
import simplejson
from zope import interface
from pyramid.response import Response
from pyramid.httpexceptions import WSGIHTTPException
from memphis.view.layout import query_layout
from memphis.view.interfaces import IRenderer


class BaseRenderer(object):
    interface.implements(IRenderer)

    factory = None

    def bind(self, factory):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.factory = factory
        return clone


class SimpleRenderer(BaseRenderer):

    def __init__(self, layout='', content_type='text/html'):
        self.layout = layout
        self.content_type = content_type

    def __call__(self, context, request, factory=None):
        response = request.response
        response.content_type = self.content_type

        if not factory:
            factory = self.factory

        try:
            view, result = factory(context, request)
        except WSGIHTTPException, resp:
            return resp

        if isinstance(result, Response):
            return result

        if self.layout is not None:
            layout = query_layout(request, context, self.layout)
            if layout is not None:
                result = layout(result, view=view)

        if type(result) is unicode:
            response.unicode_body = result
        else:
            response.body = result

        return response


class Renderer(BaseRenderer):

    def __init__(self, template, layout='', content_type='text/html'):
        self.template = template
        self.layout = layout
        self.content_type = content_type

    def __call__(self, context, request, factory=None):
        response = request.response
        response.content_type = self.content_type

        if not factory:
            factory = self.factory

        try:
            view, params = factory(context, request)
        except WSGIHTTPException, resp:
            return resp

        if isinstance(params, Response):
            return params

        kwargs = {'view': view,
                  'context': context,
                  'request': request,
                  'format': format}
        if type(params) is dict:
            kwargs.update(params)

        result = self.template(**kwargs)

        if self.layout is not None:
            layout = query_layout(request, context, self.layout)
            if layout is not None:
                result = layout(result, view=view)

        if type(result) is unicode:
            response.unicode_body = result
        else:
            response.body = result

        return response


class JSONRenderer(BaseRenderer):

    content_type = 'text/json'

    def __init__(self, content_type='text/json'):
        self.content_type = content_type

    def __call__(self, context, request, factory=None, dumps=simplejson.dumps):
        if not factory:
            factory = self.factory

        view, result = factory(context, request)

        response = request.response
        response.content_type = self.content_type
        response.body = dumps(result)
        return response


json = JSONRenderer()
