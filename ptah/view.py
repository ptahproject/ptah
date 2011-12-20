""" base view class with access to various api's """
import cgi
import logging
from zope.interface import Interface
from pyramid.decorator import reify
from pyramid.compat import string_types
from pyramid.renderers import RendererHelper
from pyramid.config.views import DefaultViewMapper

import ptah.view
from ptah import config
from ptah.formatter import format
from ptah.library import include, render_includes

log = logging.getLogger('ptah.view')

SNIPPET_ID = 'ptah.view:snippet'


class View(object):
    """ Base view """

    __name__ = ''
    __parent__ = None

    format = format

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

    @reify
    def application_url(self):
        url = self.request.application_url
        if url.endswith('/'):
            url = url[:-1]
        return url

    def update(self):
        return {}

    def __call__(self):
        result = self.update()
        if result is None:
            result = {}

        return result

    def include(self, name):
        include(self.request, name)

    def render_includes(self):
        return render_includes(self.request)

    def message(self, msg, type='info'):
        ptah.view.add_message(self.request, msg, type)

    def render_messages(self):
        return ptah.view.render_messages(self.request)

    def snippet(self, stype, context=None):
        if context is None:
            context = self.context

        request = self.request

        try:
            snippet = request.registry.queryMultiAdapter(
                (context, request), ISnippet, stype)

            if snippet is not None:
                return snippet
        except Exception as e:
            log.exception(str(e))

        return ''


class ISnippet(Interface):
    """ marker interface """


def render_snippet(name, context, request):
    """Render snippet

    :param name: Name of snippet
    :param context: Context for snippet
    :param request: Current request
    :rtype: string with rendered html

    """
    try:
        return request.registry.getMultiAdapter(
            (context, request), ISnippet, name)
    except Exception as e:
        log.exception(str(e))
        raise


class snippet(object):
    """Register snippet.

    :param name: Snippet name
    :param context: Snippet context
    :param renderer: Pyramid renderer

    Example:

    .. code-block:: python

      import ptah

      @ptah.snippet('test', Context, renderer='...:test.pt')
      def snippet(request):
          ...

      ptah.render_snippet('test', Context(), request)

    To render snippet use :py:func:`ptah.render_snippet` or
    :py:class:`ptah.View.snippet`.

    """

    def __init__(self, name, context=None, renderer=None, __depth=1):
        self.info = config.DirectiveInfo(__depth)

        self.discr = discr = (SNIPPET_ID, name, context)

        intr = config.Introspectable(SNIPPET_ID, discr, name, SNIPPET_ID)
        intr['name'] = name
        intr['context'] = context
        intr['renderer'] = renderer
        intr['module'] = self.info.module.__name__
        intr['codeinfo'] = self.info.codeinfo
        self.intr = intr

    @classmethod
    def register(cls, name, context=None, view=None, renderer=None):
        """ Register snippet.

        :param name: Snippet name
        :param context: Snippet context
        :param view: View implementation
        :param renderer: Pyramid renderer

        .. code-block:: python

          def snippet(request):
              ...

          ptah.snippet.register('test', Context, view=snippet):
              ...

        """
        return snippet(name, context, renderer, 2)(view)

    @classmethod
    def pyramid(cls, cfg, name, context=None, view=None, renderer=None):
        """ Pyramid `ptah_snippet` directive.

        :param name: Snippet name
        :param context: Snippet context
        :param view: View implementation
        :param renderer: Pyramid renderer

        .. code-block:: python

          config = Configurator()
          config.include('ptah')

          config.ptah_snippet('test', view=snippet, renderer='.../test.pt')
        """
        return snippet(name, context, renderer, 3)(view, cfg)

    def _register(self, cfg):
        intr = self.intr

        renderer = intr['renderer']
        if isinstance(renderer, string_types):
            renderer = RendererHelper(name=renderer, registry=cfg.registry)

        view = intr['view']
        if view is None:
            view = ptah.View

        # register snippet
        context = intr['context']
        if context is None:
            context = Interface

        cfg.registry.registerAdapter(
            SnippetRenderer(view, context, renderer),
            [context, Interface], ISnippet, name=intr['name'])

    def __call__(self, view, cfg=None):
        intr = self.intr
        intr['view'] = view

        self.info.attach(
            config.Action(
                self._register,
                discriminator=self.discr, introspectables=(intr,)),
            cfg)
        return view


class SnippetRenderer(object):

    def __init__(self, view, context, renderer):
        self.view = view
        self.context = context
        self.renderer = renderer

        mapper = getattr(view, '__view_mapper__', DefaultViewMapper)
        self.mapped_view = mapper()(view)

    def __call__(self, context, request):
        orig_view = getattr(request, '__view__', None)
        value = self.mapped_view(context, request)
        if self.renderer is None:
            request.__view__ = orig_view
            return value

        if value is None:
            value = {}

        system = {'view': getattr(request, '__view__', None),
                  'renderer_info': self.renderer,
                  'context': context,
                  'request': request}

        result = self.renderer.render(value, system, request)
        request.__view__ = orig_view
        return result


def add_message(request, msg, type='info'):
    """ Add status message

    Predefined message types

    * info

    * success

    * warning

    * error

    """
    message = Message(msg, request)
    try:
        msg = request.registry.getMultiAdapter(
            (message, request), ISnippet, type)
    except Exception as e:
        log = logging.getLogger('ptah.view')
        log.exception(str(e))
    request.session.flash(msg, 'status')


def render_messages(request):
    """ Render previously added messages """
    return ''.join(request.session.pop_flash('status'))


class Message(object):
    """ Message context """

    def __init__(self, message, request):
        self.message = message
        self.request = request


snippet.register(
    'info', Message, renderer='ptah.view:templates/msg-info.pt')

snippet.register(
    'success', Message, renderer='ptah.view:templates/msg-success.pt')

snippet.register(
    'warning', Message, renderer='ptah.view:templates/msg-warning.pt')


@snippet('error', Message, renderer='ptah.view:templates/msg-error.pt')
def errorMessage(context, request):
    e = context.message

    if isinstance(e, Exception):
        message = '%s: %s'%(
            e.__class__.__name__, cgi.escape(str(e), True))
    else:
        message = e

    return {'message': message}
