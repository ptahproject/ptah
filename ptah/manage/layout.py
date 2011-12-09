import inspect
import json
from collections import OrderedDict
from ptah import view
#from ptah.view.view import PyramidView

from zope.interface import providedBy
from pyramid.view import view_config
from pyramid.interfaces import IView, IViewClassifier
from pyramid.httpexceptions import HTTPNotFound


@view_config('layout-preview.html')
class LayoutPreview(view.View):

    view = None
    layout = None
    colors = ['green', 'yellow', 'blue', 'gray', 'black', 'black']

    def update(self):
        request = self.request
        context = self.context

        self.view_name = view_name = request.GET.get('view', '')

        adapters = request.registry.adapters

        view_callable = adapters.lookup(
            (IViewClassifier, providedBy(request), providedBy(context)),
            IView, name=view_name, default=None)

        if not isinstance(view_callable, PyramidView):
            raise HTTPNotFound()

        view_renderer = None
        layout_renderer = None

        for r in view_callable.renderers:
            if isinstance(r, view.LayoutRenderer):
                layout_renderer = r
            if isinstance(r, view.ViewRenderer):
                view_renderer = r

        if layout_renderer is not None:
            self.layout = view.query_layout_chain(
                context, request, layout_renderer.layout)

        self.view = view_renderer
        self.action = view_callable.__config_action__

        if self.layout is None:
            raise HTTPNotFound()

    def build_layout_info(self, layout):
        action = layout.__config_action__
        info = action.info

        data = OrderedDict(
            (('name', layout.name),
             ('parent-layout', layout.layout),
             ('class', '%s.%s'%(layout.__class__.__module__,
                                layout.__class__.__name__)),
             ('python-module', info.module.__name__),
             ('python-module-location', info.module.__file__),
             ('python-module-line', info.codeinfo[1]),
             ('template', 'unset'),
             ('context', '%s.%s'%(layout.context.__class__.__module__,
                                  layout.context.__class__.__name__)),
             ('context-path', self.request.resource_url(layout.context)),
             ))

        if layout.template:
            data['template'] = str(layout.template)

        return data

    def build_view_info(self, view):
        action = self.action
        info = action.info

        if inspect.isclass(info.context):
            factory = info.context
        else:
            factory = action.args[0]

        if inspect.isclass(factory):
            factory = '%s.%s'%(factory.__module__,
                               factory.__name__)
        else:
            factory = factory.__name__

        data = OrderedDict(
            (('name', self.view_name),
             ('view-factory', factory),
             ('python-module', info.module.__name__),
             ('python-module-location', info.module.__file__),
             ('python-module-line', info.codeinfo[1]),
             ('template', 'unset'),
             ('context', '%s.%s'%(self.context.__class__.__module__,
                                  self.context.__class__.__name__)),
             ('context-path', self.request.resource_url(self.context)),
             ))

        if hasattr(view, 'template'):
            data['template'] = str(view.template)

        return data

    def render(self):
        res = []

        content = self.view(self.context, self.request, '')
        content = '\n<!-- view:\n%s \n-->\n'\
                  '<div style="border: 2px solid red">%s</div>'%(
            json.dumps(self.build_view_info(self.view), indent=True),
            content)

        for layout in self.layout:
            layout.update()

            res = layout.render(content)
            idx = self.layout.index(layout)
            content = '\n<!-- layout:\n%s \n-->\n'\
                      '<div style="border: 4px solid %s">%s</div>'%(
                json.dumps(self.build_layout_info(layout), indent=True),
                self.colors[idx], res)

        return content
