""" layout implementation """
import sys
import json
import logging
import random
import venusian
from collections import namedtuple
from collections import OrderedDict
from zope.interface import providedBy, Interface
from pyramid.compat import text_, string_types
from pyramid.config.views import DefaultViewMapper
from pyramid.location import lineage
from pyramid.registry import Introspectable
from pyramid.renderers import RendererHelper
from pyramid.interfaces import IRequest, IResponse, IRouteRequest

log = logging.getLogger('ptah.renderer')

LAYOUT_ID = 'ptah.renderer:layout'

LayoutInfo = namedtuple(
    'LayoutInfo', 'name layout view original renderer intr')

CodeInfo = namedtuple(
    'Codeinfo', 'filename lineno function source module')


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


def add_layout(cfg, name='', context=None, root=None, parent=None,
               renderer=None, route_name=None, use_global_views=True,
               view=None):
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
    :param view: View callable


    Simple example with one default layout and 'page' layout.

    .. code-block:: python

      class PageLayout(object):
           ...

      config.add_layout('page', parent='page', renderer='my_package:template/page.pt')


    To use layout with pyramid view use ``renderer=ptah.renderer.layout('my_pkg:template/page.pt')``

    Example:

    .. code-block:: python

      config.add_view('
          index.html',
          renderer = ptah.renderer.layout('...'))

    in this example '' layout is beeing used. You can specify specific layout
    name for pyramid view ``ptah.renderer.layout('page', 'layout name')``

    """
#    (scope, module,
#     f_locals, f_globals, codeinfo) = venusian.getFrameInfo(sys._getframe(2))

#    codeinfo = CodeInfo(
#        codeinfo[0], codeinfo[1], codeinfo[2], codeinfo[3], module.__name__)

    discr = (LAYOUT_ID, name, context, route_name)

    intr = Introspectable(LAYOUT_ID, discr, name, 'ptah.renderer_layout')

    intr['name'] = name
    intr['context'] = context
    intr['root'] = root
    intr['renderer'] = renderer
    intr['route_name'] = route_name
    intr['parent'] = parent
    intr['use_global_views'] = use_global_views
    intr['view'] = view
#    intr['codeinfo'] = codeinfo

    if not parent:
        parent = None
    elif parent == '.':
        parent = ''

    if isinstance(renderer, string_types):
        renderer = RendererHelper(name=renderer, registry=cfg.registry)

    if context is None:
        context = Interface

    def register():
        request_iface = IRequest
        if route_name is not None:
            request_iface = cfg.registry.getUtility(
                IRouteRequest, name=route_name)

        if use_global_views:
            request_iface = Interface

        mapper = getattr(view, '__view_mapper__', DefaultViewMapper)
        mapped_view = mapper()(view)

        info = LayoutInfo(name, parent, mapped_view, view, renderer, intr)
        cfg.registry.registerAdapter(
            info, (root, request_iface, context), ILayout, name)

    cfg.action(discr, register, introspectables=(intr,))


class LayoutRenderer(object):

    def __init__(self, layout):
        self.layout = layout

    def layout_info(self, layout, context, request, content,
                    colors=('green','blue','yellow','gray','black')):
        intr = layout.intr
        view = intr['view']
        if view is not None:
            layout_factory = '%s.%s'%(view.__module__, view.__name__)
        else:
            layout_factory = 'None'

        data = OrderedDict(
            (('name', intr['name']),
             ('parent-layout', intr['parent']),
             ('layout-factory', layout_factory),
#             ('python-module', intr['codeinfo'].module),
#             ('python-module-location', intr['codeinfo'].filename),
#             ('python-module-line', intr['codeinfo'].lineno),
             ('renderer', intr['renderer']),
             ('context', '%s.%s'%(context.__class__.__module__,
                                  context.__class__.__name__)),
             ('context-path', request.resource_url(context)),
             ))

        content = text_('\n<!-- layout:\n%s \n-->\n'\
                        '<div style="border: 2px solid %s">%s</div>')%(
            json.dumps(data, indent=2), random.choice(colors), content)

        return content

    def __call__(self, content, context, request):
        chain = query_layout_chain(request.root, context, request, self.layout)
        if not chain:
            log.warning(
                "Can't find layout '%s' for context '%s'",
                self.layout, context)
            return content

        value = request.layout_data

        for layout, layoutcontext in chain:
            if layout.view is not None:
                vdata = layout.view(layoutcontext, request)
                if IResponse.providedBy(vdata):
                    return vdata
                if vdata is not None:
                    value.update(vdata)

            system = {'view': getattr(request, '__view__', None),
                      'renderer_info': layout.renderer,
                      'context': layoutcontext,
                      'request': request,
                      'content': content,
                      'wrapped_content': content}

            content = layout.renderer.render(value, system, request)

            if getattr(request, '__layout_debug__', False):
                content = self.layout_info(
                    layout, layoutcontext, request, content)

        return content


def set_layout_data(request, **kw):
    request.layout_data.update(kw)


class layout(RendererHelper):

    package = None
    renderer = None
    type = 'ptah.renderer:layout'

    def __init__(self, name='', layout=''):
        self.name = name
        self.layout_name = layout

    def render(self, value, system_values, request=None):
        renderer = self.renderer
        context = system_values.get('context', None)
        try:
            layout = self.layout
            registry = self.registry
        except AttributeError:
            layout = self.layout = LayoutRenderer(self.layout_name)
            registry = self.registry = request.registry
            if self.name:
                renderer = self.renderer = RendererHelper(
                    self.name, registry=registry)

        if renderer:
            value = renderer.render(value, system_values, request)

        return layout(value, context, request)

    def render_to_response(self, value, system_values, request=None):
        result = self.render(value, system_values, request=request)
        if IResponse.providedBy(result):
            return result
        return self._make_response(result, request)


class layout_config(object):

    def __init__(self, name='', context=None, root=None, parent=None,
                 renderer=None, route_name=None, use_global_views=True):
        self.name = name
        self.context = context
        self.root = root
        self.parent = parent
        self.renderer = renderer
        self.route_name = route_name
        self.use_global_views = use_global_views

    def __call__(self, wrapped):
        def callback(context, name, ob):
            cfg = context.config.with_package(info.module)
            add_layout(cfg, self.name, self.context,
                       self.root, self.parent,
                       self.renderer, self.route_name,
                       self.use_global_views, ob)

        info = venusian.attach(wrapped, callback, category='ptah.renderer')

        return wrapped
