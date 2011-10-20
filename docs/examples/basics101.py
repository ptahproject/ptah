""" A route and 2 views for Content """

import cgi
from paste.httpserver import serve
from ptah import view, cms


view.register_route('show_models', '/show_models')

@view.pview(route='show_models')
def show_models(request):
    models = cms.Session.query(cms.Content).all()
    return cgi.escape(str(models))

@view.pview('show_info', context=cms.Content)
def show_info(context, request):
    return cgi.escape(str(context.info()))

@view.pview('list_children', context=cms.Container)
def list_children(context, request):
    out = []
    for name, child in context.items():
        if isinstance(child, cms.Container):
            href = '<a href="%slist_children">%s</a>' #XXX extra /?
            href = href % (request.resource_url(child), child.title)
        else:
            href = '<a href="%sshow_info">%s</a>'
            href = href % (request.resource_url(child), child.title)
        out.append(href)
    return '<br />'.join(out)

if __name__ == '__main__':
    """ need to point to your settings.ini file in make_wsgi_app call.
        http://localhost:8080/show_models is url dispatch function.
        http://localhost:8080/list_children is traverser on context
        $resource_url/show_info on either folder or content.
    """
    import ptah
    app = ptah.make_wsgi_app({'settings':r'./ptah.ini'})
    serve(app, host='0.0.0.0')
