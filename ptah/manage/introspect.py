""" introspect module """
import urllib
from zope.interface import Interface
from pyramid.view import view_config
from pyramid.compat import string_types, url_unquote
from pyramid.interfaces import IIntrospectable

import ptah
from ptah.view import ISnippet
from ptah.manage import get_manage_url


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
    renderer='ptah.manage:templates/introspect.pt')
class MainView(ptah.View):
    __doc__ = 'Introspection module view.'

    def update(self):
        self.manage_url = '{0}/introspect'.format(get_manage_url(self.request))

        self.renderers = sorted(
            (self.request.registry.adapters.lookupAll(
                (IIntrospectable, Interface), ISnippet)),
            key = lambda item: item[1].view.title)


@view_config(
    context=Introspector, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/introspect-intr.pt')
class IntrospectorView(ptah.View):

    def update(self):
        name = self.context.name
        registry = self.request.registry

        self.renderer = registry.adapters.lookup(
            (IIntrospectable, Interface), ISnippet, name=name)

        self.intrs = sorted(
            (item['introspectable'] for item in
             registry.introspector.get_category(name)),
            key = lambda item: item.title)

        self.manage_url = '{0}/introspect'.format(get_manage_url(self.request))

        self.renderers = sorted(
            (registry.adapters.lookupAll(
                (IIntrospectable, Interface), ISnippet)),
            key = lambda item: item[1].view.title)
