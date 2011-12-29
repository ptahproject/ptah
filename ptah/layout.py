""" layout implementation """
import json
import logging
import random
import inspect
from collections import namedtuple
from collections import OrderedDict
from zope.interface import providedBy, Interface

from pyramid.compat import text_, string_types
from pyramid.config.views import DefaultViewMapper
from pyramid.httpexceptions import HTTPException
from pyramid.location import lineage
from pyramid.renderers import RendererHelper
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IView
from pyramid.interfaces import IViewClassifier

from ptah import config
from ptah.view import View

log = logging.getLogger('ptah')

LAYOUT_ID = 'ptah.view:layout'
LAYOUT_WRAPPER_ID = 'ptah.view:layout-wrapper'

LayoutInfo = namedtuple(
    'LayoutInfo', 'name layout view original renderer intr')


class ILayout(Interface):
    """ marker interface """


def query_layout(root, context, request, name=''):
    """ query named layout for context """
    assert IRequest.providedBy(request), "must pass in a request object"

    try:
        iface = request.request_iface
    except AttributeError:
        iface = IRequest

    root = providedBy(root)

    adapters = request.registry.adapters

    for context in lineage(context):
        layout_factory = adapters.lookup(
            (root, iface, providedBy(context)), ILayout, name=name)

        if layout_factory is not None:
            return layout_factory, context

    return None, None


def query_layout_chain(root, context, request, layoutname=''):
    chain = []

    layout, layoutcontext = query_layout(root, context, request, layoutname)
    if layout is None:
        return chain

    chain.append((layout, layoutcontext))
    contexts = {layoutname: layoutcontext}

    while layout is not None and layout.layout is not None:
        if layout.layout in contexts:
            l_context = contexts[layout.layout].__parent__
        else:
            l_context = context

        layout, layoutcontext = query_layout(
            root, l_context, request, layout.layout)
        if layout is not None:
            chain.append((layout, layoutcontext))
            contexts[layout.name] = layoutcontext

            if layout.layout is None:
                break

    return chain


class layout(object):
    """Registers a layout.

    :param name: Layout name
    :param context: Specific context for this layout.
    :param root:  Root object
    :param parent: A parent layout. None means no parent layout.
    :param renderer: A pyramid renderer
    :param route_name: A pyramid route_name. Apply layout only for
        specific route
    :param use_global_views: Apply layout to all routes. even is route
        doesnt use use_global_views.


    Simple example with one default layout and 'page' layout.

    .. code-block:: python

      import ptah

      @ptah.layout('page', parent='page', renderer='ptah:template/page.pt')
      class PageLayout(ptah.View):
           ...

      @ptah.layout('', parent='page', renderer='ptah:template/template.pt')
      class DefaultLayout(object):
           ...

    To use layout with pyramid view use ``wrapper=ptah.wrap_layout()``

    Example:

    .. code-block:: python

      config.add_view('
          index.html',
          wrapper=ptah.wrap_layout(),
          renderer = '...')

    in this example '' layout is beeing used. You can specify specific layout
    name for pyramid view ``ptah.wrap_layout('page')``

    """

    def __init__(self, name='', context=None, root=None, parent=None,
                 renderer=None, route_name=None, use_global_views=False,
                 __depth=1):
        self.info = config.DirectiveInfo(__depth)
        self.discr = (LAYOUT_ID, name, context, route_name)

        self.intr = intr = config.Introspectable(
            LAYOUT_ID, self.discr, name, LAYOUT_ID)

        intr['name'] = name
        intr['context'] = context
        intr['root'] = root
        intr['renderer'] = renderer
        intr['route_name'] = route_name
        intr['parent'] = parent
        intr['use_global_views'] = use_global_views
        intr['codeinfo'] = self.info.codeinfo

    @classmethod
    def register(cls, name='', context=None, root=None, parent='',
                 renderer=None, route_name=None, use_global_views=False,
                 view=View):
        """ Imperative layout registration.

        :param name: Layout name
        :param context: Specific context for this layout.
        :param root:  Root object
        :param parent: A parent layout. None means no parent layout.
        :param renderer: A pyramid renderer
        :param route_name: A pyramid route_name. Apply layout only for
            specific route
        :param use_global_views: Apply layout to all routes. even is route
            doesnt use use_global_views.
        :param view: Layout implementation (same as for pyramid view)

        .. code-block:: python

            ptah.layout.register('page', renderer='...', view=MyLayout)

        """
        layout(name, context, root, parent,
               renderer, route_name, use_global_views, 2)(view)

    @classmethod
    def pyramid(cls, cfg, name='', context=None, root=None, parent='',
                renderer=None, route_name=None,
                use_global_views=False, view=View):
        """ Pyramid `ptah_layout` directive:

        .. code-block:: python

          config = Configurator()
          config.include('ptah')

          config.ptah_layout('page', renderer='..')
        """
        l = layout(name, context, root, parent,
               renderer, route_name, use_global_views, 3)(view, cfg)

    def __call__(self, view, cfg=None):
        intr = self.intr
        intr['view'] = view

        self.info.attach(
            config.Action(
                self._register,
                discriminator=self.discr, introspectables=(intr,)),
            cfg)
        return view

    def _register(self, cfg):
        intr = self.intr

        view, name, context, root, \
              renderer, layout, route_name, use_global_views = \
              (intr['view'], intr['name'], intr['context'], intr['root'],
               intr['renderer'], intr['parent'], intr['route_name'],
               intr['use_global_views'])

        if not layout:
            layout = None
        elif layout == '.':
            layout = ''

        if isinstance(renderer, string_types):
            renderer = RendererHelper(name=renderer, registry=cfg.registry)

        request_iface = IRequest
        if route_name is not None:
            request_iface = cfg.registry.getUtility(
                IRouteRequest, name=route_name)

        if use_global_views:
            request_iface = Interface

        if context is None:
            context = Interface

        mapper = getattr(view, '__view_mapper__', DefaultViewMapper)
        mapped_view = mapper()(view)

        info = LayoutInfo(
            name, layout, mapped_view, view, renderer, intr)
        cfg.registry.registerAdapter(
            info, (root, request_iface, context), ILayout, name)


class LayoutRenderer(object):

    def __init__(self, layout):
        self.layout = layout

    def layout_info(self, layout, context, request, content,
                    colors=('green','blue','yellow','gray','black')):
        intr = layout.intr
        view = intr['view']

        data = OrderedDict(
            (('name', intr['name']),
             ('parent-layout', intr['parent']),
             ('layout-factory', '%s.%s'%(view.__module__, view.__name__)),
             ('python-module', intr['codeinfo'].module),
             ('python-module-location', intr['codeinfo'].filename),
             ('python-module-line', intr['codeinfo'].lineno),
             ('renderer', intr['renderer']),
             ('context', '%s.%s'%(context.__class__.__module__,
                                  context.__class__.__name__)),
             ('context-path', request.resource_url(context)),
             ))

        content = text_('\n<!-- layout:\n%s \n-->\n'\
                        '<div style="border: 2px solid %s">%s</div>')%(
            json.dumps(data, indent=2), random.choice(colors), content)

        return content

    def view_info(self, discr, context, request, content):
        introspector = request.registry.introspector

        template = 'unknown'
        intr = introspector.get('templates', discr)
        if intr is not None: # pragma: no cover
            template = intr['name']

        intr = introspector.get('views', discr)
        if intr is None: # pragma: no cover
            return content

        view = intr['callable']

        data = OrderedDict(
            (('name', intr['name']),
             ('route-name', intr['route_name']),
             ('view-factory', '%s.%s'%(view.__module__, view.__name__)),
             ('python-module', inspect.getmodule(view).__name__),
             ('python-module-location', inspect.getsourcefile(view)),
             ('python-module-line', inspect.getsourcelines(view)[-1]),
             ('renderer', template),
             ('context', '%s.%s'%(context.__class__.__module__,
                                  context.__class__.__name__)),
             ('context-path', request.resource_url(context)),
             ))

        content = text_('\n<!-- view:\n%s \n-->\n'\
                        '<div style="border: 2px solid red">%s</div>')%(
            json.dumps(data, indent=2), content)

        return content

    def __call__(self, context, request):
        chain = query_layout_chain(request.root, context, request, self.layout)
        if not chain:
            log.warning("Can't find layout '%s' for context '%s'",
                        self.layout, context)

        if isinstance(request.wrapped_response, HTTPException):
            return request.wrapped_response

        debug = getattr(request, '__layout_debug__', False)

        content = text_(request.wrapped_body, 'utf-8')

        if debug:
            content = self.view_info(debug, context, request, content)

        for layout, layoutcontext in chain:
            value = layout.view(layoutcontext, request)
            if value is None:
                value = {}

            system = {'view': request.__view__,
                      'renderer_info': layout.renderer,
                      'context': layoutcontext,
                      'request': request,
                      'wrapped_content': content}

            content = layout.renderer.render(value, system, request)

            if debug:
                content = self.layout_info(
                    layout, layoutcontext, request, content)

        request.response.text = content
        return request.response


def wrap_layout(layout=''):
    """ Generate view name for pyramid view declaration.

    .. code-block:: python

      config = Configurator()
      config.include('ptah')

      config.ptah_layout('page')

      config.add_view(
          'index.html',
          wrapper=ptah.wrap_layout())

    """
    name = '#layout-{0}'.format(layout)

    info = config.DirectiveInfo()
    info.attach(config.Action(wrap_layout_impl, (name, layout)))
    return name


def wrap_layout_impl(cfg, name, layout):
    renderer = cfg.registry.adapters.lookup(
        (IViewClassifier, Interface, Interface), IView, name=name)
    if renderer is None:
        cfg.registry.registerAdapter(
            LayoutRenderer(layout),
            (IViewClassifier, Interface, Interface), IView, name)
