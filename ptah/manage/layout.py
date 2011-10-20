from ptah import view, config
from ptah.view.renderers import BaseRenderer

from zope.interface import providedBy
from pyramid.interfaces import IView, IViewClassifier


class LayoutPreview(view.View):
    view.pview('layout-preview.html', layout=None)

    template = None
    layout_chain = ()
    colors = ['green', 'yellow', 'blue', 'gray', 'black', 'black']

    def update(self):
        request = self.request
        context = self.context

        view_name = request.GET.get('view', '')
        
        adapters = config.registry.adapters

        view_callable = adapters.lookup(
            (IViewClassifier, providedBy(request), providedBy(context)),
            IView, name=view_name, default=None)
        
        renderer = None

        if isinstance(view_callable, BaseRenderer):
            renderer = view_callable
        else:
            for cell in view_callable.func_closure:
                if isinstance(cell.cell_contents, BaseRenderer):
                    renderer = cell.cell_contents
                    break

        layout = getattr(renderer, 'layout', None)
        self.factory = getattr(renderer, 'factory', None)
        self.template = getattr(renderer, 'template', None)

        if layout is not None:
            layout_chain = []

            parent = context
            
            l = view.query_layout(request, parent, layout)
            layout_chain.append(l)

            while l is not None:
                if l.layout is None:
                    break

                parent = l.__parent__ or parent
                l = view.query_layout(request, parent, l.layout)
                layout_chain.append(l)

            self.layout_chain = layout_chain

    def render(self):
        res = []

        view, params = self.factory(self.context, self.request)

        kwargs = {'view': view,
                  'context': self.context,
                  'request': self.request}
        if type(params) is dict:
            kwargs.update(params)
            
        if self.template:
            res = self.template(**kwargs)
        else:
            res = view.render()
            
        content = u'<div style="border: 2px solid red">%s</div>'%res
        for layout in self.layout_chain:
            layout.update()
            res = layout.render(content)
            idx = self.layout_chain.index(layout)
            content = u'<div style="border: 4px solid %s">%s</div>'%(
                self.colors[idx], res)

        return content
