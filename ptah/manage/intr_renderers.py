""" introspector renderers """
import sys
import inspect
from pyramid.renderers import render
from pyramid.interfaces import IIntrospectable

import ptah
from ptah import config, manage, form
from ptah.manage import get_manage_url
from ptah.form.field import PREVIEW_ID


class Renderer(ptah.View):

    title = ''
    rst_to_html = staticmethod(ptah.rst_to_html)

    def __call__(self):
        return {'manage_url': get_manage_url(self.request)}


@ptah.snippet(
    ptah.event.ID_EVENT, IIntrospectable,
    renderer='ptah.manage:templates/intr-event.pt')
class EventRenderer(Renderer):
    """ List of event declarations """

    title = 'Events'


@ptah.snippet(
    'ptah.config:subscriber', IIntrospectable,
    renderer='ptah.manage:templates/intr-subscriber.pt')
class SubscriberRenderer(Renderer):
    """ List of event subscribers """

    title = 'Event subscribers'

    def getInfo(self):
        intr = self.context
        handler = intr['handler']
        required = intr['required']
        factoryInfo = '%s.%s'%(intr['codeinfo'].module, handler.__name__)

        if len(required) > 1: # pragma: no cover
            obj = required[0]
            klass = required[1]
            #event = config.get_cfg_storage(config.ID_EVENT).get(
            #    action.args[1][-1], None)
        else:
            obj = None
            klass = required[0]
            #event = config.get_cfg_storage(config.ID_EVENT).get(
            #    action.args[1][0], None)

        return locals()


@ptah.snippet(
    'ptah:permission', IIntrospectable,
    renderer='ptah.manage:templates/intr-permission.pt')
class PermissionRenderer(Renderer):
    """ Permission registrations """

    title = 'Permission'


@ptah.snippet(
    'ptah:role', IIntrospectable,
    renderer='ptah.manage:templates/intr-role.pt')
class RoleIntrospection(Renderer):
    """ Role registrations """

    title = 'Role'


@ptah.snippet(
    'ptah:resolver', IIntrospectable,
    renderer='ptah.manage:templates/intr-uriresolver.pt')
class UriRenderer(Renderer):
    """ Uri resolvers """

    title = 'Uri resolver'


@ptah.snippet(
    'ptah.manage:module', IIntrospectable,
    renderer='ptah.manage:templates/intr-managemodule.pt')
class ManageModuleRenderer(Renderer):
    """ List of registered ptah manage modules """

    title = 'Ptah manage modules'


@ptah.snippet(
    'ptah:aclmap', IIntrospectable,
    renderer='ptah.manage:templates/intr-aclmap.pt')
class ACLMapRenderer(Renderer):
    """ ACL map registration """

    title = 'ACL Maps'


@ptah.snippet(
    'ptah:authchecker', IIntrospectable,
    renderer='ptah.manage:templates/intr-authchecker.pt')
class AuthCheckerRenderer(Renderer):
    """ List of registered authentication checkers """

    title = 'Authentication checkers'


@ptah.snippet(
    'ptah:authprovider', IIntrospectable,
    renderer='ptah.manage:templates/intr-authprovider.pt')
class AuthProviderRenderer(Renderer):
    """ List of registered authentication providers """

    title = 'Authentication providers'


@ptah.snippet(
    'ptah:settings-group', IIntrospectable,
    renderer='ptah.manage:templates/intr-settings.pt')
class SettingsGroupRenderer(Renderer):
    """ List of registered settings groups """

    title = 'Settings'


@ptah.snippet(
    'ptah.form:field', IIntrospectable,
    renderer='ptah.manage:templates/intr-field.pt')
class FieldRenderer(Renderer):
    """ List of registered fields """

    title = 'Fields'

    def __call__(self):
        return {'manage_url': get_manage_url(self.request),
                'previews': config.get_cfg_storage(PREVIEW_ID)}


@ptah.snippet(
    'ptah:uiaction', IIntrospectable,
    renderer='ptah.manage:templates/intr-uiaction.pt')
class uiActionRenderer(Renderer):
    """ List of registered ui actions """

    title = 'UI Actions'


@ptah.snippet(
    'ptah:token-type', IIntrospectable,
    renderer='ptah.manage:templates/intr-tokentype.pt')
class TokenTypeRenderer(Renderer):
    """ List of registered token types """

    title = 'Token types'


@ptah.snippet(
    'ptah.cms:type', IIntrospectable,
    renderer='ptah.manage:templates/intr-contenttype.pt')
class ContentTypeRenderer(Renderer):
    """ Ptah content types """

    title = 'Content Types'


@ptah.snippet(
    'ptah:formatter', IIntrospectable,
    renderer='ptah.manage:templates/intr-formatter.pt')
class formatterRenderer(Renderer):
    """ List of formatters """

    title = 'Formatters'
