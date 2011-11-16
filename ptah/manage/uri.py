""" uri resolve """
import inspect
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import form, view, config, manage
from ptah.uri import RESOLVER_ID

from manage import PtahManageRoute


class UriResolver(form.Form):
    view.pview('uri.html', context = PtahManageRoute,
               template = view.template('ptah.manage:templates/uri.pt'))

    fields = form.Fieldset(
        form.LinesField(
            'uri',
            title = 'Uri',
            description = "List of uri's",
            klass = 'xxlarge'))

    uri = None
    rst_to_html = staticmethod(ptah.rst_to_html)

    def form_content(self):
        return {'uri': [self.request.GET.get('uri','')]}

    @form.button('Show', actype=form.AC_PRIMARY)
    def show_handler(self):
        data, errors = self.extract()
        if errors:
            self.message(errors, 'form-error')
        else:
            self.uri = data['uri']

    def update(self):
        super(UriResolver, self).update()

        uri = self.uri
        if uri is None:
            uri = [self.request.GET.get('uri','')]

        resolvers = config.get_cfg_storage(RESOLVER_ID)

        self.data = data = []
        for u in uri:
            if u:
                schema = ptah.extract_uri_schema(u)
                resolver = resolvers.get(schema)
                info = {'uri': u,
                        'resolver': None,
                        'module': None,
                        'line': None,
                        'obj': None,
                        'cls': None,
                        'clsdoc': None}

                if resolver is not None:
                    info['resolver'] = resolver.__name__
                    info['r_doc'] = ptah.rst_to_html(resolver.__doc__ or u'')
                    info['module'] = resolver.__module__
                    info['name'] = '%s.%s'%(
                        resolver.__module__, resolver.__name__)
                    info['line'] = inspect.getsourcelines(resolver)[-1]

                    obj = ptah.resolve(u)
                    info['obj'] = obj

                    if obj is not None:
                        cls = getattr(obj, '__class__', None)
                        info['cls'] = cls
                        info['clsdoc'] = ptah.rst_to_html(
                            getattr(cls, '__doc__', u'') or u'')

                        if cls is not None:
                            info['clsmod'] = cls.__module__
                            info['clsline'] = inspect.getsourcelines(cls)[-1]

                data.append(info)


class UriIntrospection(object):
    """ uri introspection view """

    title = 'Uri resolver'
    manage.introspection('ptah:uri-resolver')

    tmpl = view.template('ptah.manage:templates/directive-uriresolver.pt')

    def __init__(self, request):
        self.request = request

    def renderActions(self, *actions):
        return self.tmpl(
            actions = actions,
            rst_to_html = ptah.rst_to_html,
            manage_url = manage.CONFIG.manage_url,
            request = self.request)
