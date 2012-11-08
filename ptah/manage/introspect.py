""" introspect module """
import player
from player import RendererNotFound
from pyramid.view import view_config
from pyramid.compat import url_unquote

import ptah
from ptah.manage import get_manage_url
from pform.directives import ID_PREVIEW


@ptah.manage.module('introspect')
class IntrospectModule(ptah.manage.PtahModule):
    __doc__ = 'Insight into all configuration and registrations.'

    title = 'Introspect'

    def __getitem__(self, key):
        key = url_unquote(key)
        if key in self.request.registry.introspector.categories():
            return Introspector(key, self, self.request)

        raise KeyError(key)


class Introspector(object):

    def __init__(self, name, mod, request):
        self.__name__ = name
        self.__parent__ = mod

        self.name = name
        self.request = request


@view_config(
    context=IntrospectModule, wrapper=ptah.wrap_layout(),
    renderer='ptah-manage:introspect.lt')
class MainView(ptah.View):
    __doc__ = 'Introspection module view.'

    def update(self):
        registry = self.request.registry
        self.categories = registry.introspector.categories()
        self.manage_url = '{0}/introspect'.format(get_manage_url(self.request))


@view_config(
    context=Introspector, wrapper=ptah.wrap_layout(),
    renderer='ptah-manage:introspect-intr.lt')
class IntrospectorView(ptah.View):

    def update(self):
        name = self.context.name
        registry = self.request.registry

        self.intrs = sorted(
            (item['introspectable'] for item in
             registry.introspector.get_category(name)),
            key = lambda item: item.title)

        self.manage_url = '{0}/introspect'.format(get_manage_url(self.request))

        self.categories = registry.introspector.categories()

    def render_intr(self, intr):
        try:
            return self.request.render_tmpl(
                'ptah-intr:%s'%intr.type_name, intr,
                manage_url = self.manage_url, rst_to_html = ptah.rst_to_html)
        except RendererNotFound:
            return self.request.render_tmpl(
                'ptah-intr:ptah-default', intr,
                manage_url = self.manage_url, rst_to_html = ptah.rst_to_html)


@player.tmpl_filter('ptah-intr:pform-field')
def tmpl_formfield(context, request):
    return {'previews': request.registry[ID_PREVIEW]}


@player.tmpl_filter('ptah-intr:ptah-subscriber')
def tmpl_subscriber(intr, request):
    handler = intr['handler']
    required = intr['required']
    factoryInfo = '%s.%s'%(intr['codeinfo'].module, handler.__name__)

    if len(required) > 1: # pragma: no cover
        obj = required[0]
        klass = required[1]
    else:
        obj = None
        klass = required[0]

    return dict(factoryInfo=factoryInfo, obj=obj, klass=klass)
