from ptah import view, config
from ptah.view.view import PyramidView

from zope.interface import providedBy
from pyramid.interfaces import IView, IViewClassifier
from pyramid.httpexceptions import HTTPNotFound


class LayoutPreview(view.View):
    view.pview('layout-preview.html', layout=None)

    view = None
    layout = None
    colors = ['green', 'yellow', 'blue', 'gray', 'black', 'black']

    def update(self):
        request = self.request
        context = self.context

        view_name = request.GET.get('view', '')

        adapters = config.registry.adapters

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

        if self.layout is None:
            raise HTTPNotFound()

    def render(self):
        res = []

        content = self.view(self.context, self.request, '')

        content = u'<div style="border: 2px solid red">%s</div>'%content

        for layout in self.layout:
            layout.update()
            res = layout.render(content)
            idx = self.layout.index(layout)
            content = u'<div style="border: 4px solid %s">%s</div>'%(
                self.colors[idx], res)

        return content
