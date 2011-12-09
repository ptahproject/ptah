""" introspect module """
import urllib
from pyramid.view import view_config
from pyramid.compat import string_types

import ptah
from ptah import config, view, manage
from ptah.manage import intr_renderer, get_manage_url
from ptah.manage.manage import INTROSPECT_ID


@manage.module('introspect')
class IntrospectModule(manage.PtahModule):
    __doc__ = 'Insight into all configuration and registrations.'

    title = 'Introspect'

    def __getitem__(self, key):
        key = urllib.unquote(key)
        if key in self.request.registry.introspector.categories():
            return Introspector(key, self, self.request)

        raise KeyError(key)


class Introspector(object):

    def __init__(self, name, mod, request):
        self.__name__ = name
        self.__parent__ = mod

        self.name = name
        self.request = request

        intros = config.get_cfg_storage(INTROSPECT_ID)
        self.renderer = intros[name](request)

        self.intrs = sorted((item['introspectable'] for item in
                             self.request.registry
                             .introspector.get_category(name)),
                            key = lambda item: item.title)

        self.manage_url = '{0}/introspect'.format(get_manage_url(self.request))
        self.renderers = sorted(
            (item['introspectable']['factory'] for item in
             self.request.registry.introspector.get_category(INTROSPECT_ID)),
            key = lambda item: item.title)


@view_config(
    context=IntrospectModule, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/introspect.pt')
class MainView(view.View):
    __doc__ = 'Introspection module view.'

    def update(self):
        self.manage_url = '{0}/introspect'.format(get_manage_url(self.request))
        self.renderers = sorted(
            (item['introspectable']['factory'] for item in
             self.request.registry.introspector.get_category(INTROSPECT_ID)),
            key = lambda item: item.title)


@view_config(
    context=Introspector, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/introspect-intr.pt')
class IntrospectorView(view.View):
    pass
