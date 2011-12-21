import inspect
from zope.interface import providedBy
from pyramid.view import view_config
from pyramid.interfaces import IView, IViewClassifier
from pyramid.httpexceptions import HTTPNotFound


@view_config('layout-preview.html')
def layoutPreview(context, request):
    view_name = request.GET.get('view', '')

    adapters = request.registry.adapters

    view = adapters.lookup(
        (IViewClassifier, providedBy(request), providedBy(context)),
        IView, name=view_name, default=None)

    if view is None:
        return HTTPNotFound()

    request.__layout_debug__ = view.__discriminator__(context, request)

    return view(context, request)
