""" introspector renderers """
import sys
import inspect

import ptah
from ptah import config, view, manage, form
from ptah.manage import intr_renderer, get_manage_url
from ptah.manage.manage import INTROSPECT_ID
from ptah.form.field import PREVIEW_ID


class Renderer(object):

    title = ''
    template = None
    rst_to_html = staticmethod(ptah.rst_to_html)

    def __init__(self, request):
        self.request = request
        self.manage_url = get_manage_url(request)

    def __call__(self, intr):
        return self.template(
            intr = intr,
            view = self,
            request = self.request)


@intr_renderer(ptah.config.ID_EVENT)
class EventRenderer(Renderer):
    """ List of event declarations """

    title = 'Events'
    template = 'ptah.manage:templates/intr-event.pt'


@intr_renderer('ptah.config:adapter')
class AdapterDirective(object):
    """ List of adapter registrations """

    title = 'zc adapters'
    actions = 'ptah.manage:templates/directive-adapter.pt'

    def __init__(self, request):
        self.request = request

    def getInfo(self, action):
        context = action.info.context

        if inspect.isclass(context):
            isclass = True
            requires, name = action.args[:2]
        else:
            context = action.args[1]
            requires = action.args[2]
            name = action.kw['name']

        provided = list(interface.implementedBy(context))
        if len(provided):
            iface = provided[0]
        else: # pragma: no cover
            iface = 'unknown'

        return {'iface': iface,
                'context': context,
                'provided': provided,
                'name': name,
                'requires': requires}

    def renderActions(self, *actions):
        return self.actions(
            actions = actions,
            getInfo = self.getInfo,
            manage = get_manage_url(self.request),
            request = self.request)


@intr_renderer('ptah.view:snippettype')
class SnippetTypeDirective(Renderer):
    """ Ptah snippet types """

    title = 'Snippet Types'
    template = 'ptah.manage:templates/intr-snippettype.pt'


@intr_renderer('ptah.view:route')
class RouteDirective(Renderer):
    """ pyramid routes """

    title = 'Routes'
    actions = 'ptah.manage:templates/directive-route.pt'

    def renderActions(self, *actions):
        return self.actions(
            actions = actions,
            manage = get_manage_url(self.request),
            request = self.request)


@intr_renderer('ptah.config:subscriber')
class SubscriberRenderer(Renderer):
    """ List of event subscribers """

    title = 'Event subscribers'
    template = 'ptah.manage:templates/intr-subscriber.pt'

    def getInfo(self, intr):
        handler = intr['handler']
        required = intr['required']
        factoryInfo = '%s.%s'%(intr['codeinfo'].module, handler.__name__)

        if len(required) > 1:
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


@intr_renderer('ptah.view:view')
class ViewDirective(object):
    """ Pyramid views """

    title = 'Views'
    actions = 'ptah.manage:templates/directive-view.pt'

    def __init__(self, request):
        self.request = request

    def getInfo(self, action):
        info = action.info
        factory = action.info.context

        if inspect.isclass(factory):
            isclass = True
            name,context,template,route,layout,permission,intr=action.args
        else:
            isclass = False
            factory,name,context,template,route,layout,\
                permission,intr=action.args

        if route:
            if name:
                view = 'view: "%s" route: "%s"'%((name or '<default>'), route)
            else:
                view = 'route: "%s"'%route
        else:
            view = 'view: %s'%(name or '<default>')

        if isclass:
            factoryInfo = '%s.%s'%(factory.__module__, factory.__name__)
        else:
            factoryInfo = '%s.%s'%(info.module.__name__, factory.__name__)

        if template:
            template = template.spec
        else:
            template = ''

        return locals()

    def renderActions(self, *actions):
        return self.actions(
            getInfo = self.getInfo,
            actions = actions,
            manage = get_manage_url(self.request),
            request = self.request)


@intr_renderer('ptah:permission')
class PermissionRenderer(Renderer):
    """ Permission registrations """

    title = 'Permission'
    template = 'ptah.manage:templates/intr-permission.pt'


@intr_renderer('ptah:role')
class RoleIntrospection(Renderer):
    """ Role registrations """

    title = 'Role'
    template = 'ptah.manage:templates/intr-role.pt'


@intr_renderer('ptah:resolver')
class UriRenderer(Renderer):
    """ Uri resolvers """

    title = 'Uri resolver'
    template = 'ptah.manage:templates/intr-uriresolver.pt'


@intr_renderer('ptah.manage:module')
class ManageModuleRenderer(Renderer):
    """ List of registered ptah manage modules """

    title = 'Ptah manage modules'
    template = 'ptah.manage:templates/intr-managemodule.pt'


@intr_renderer('ptah.manage:irenderer')
class IntrospectorRenderer(Renderer):
    """ List of registered introspector renderers """

    title = 'Ptah introspector renderers'
    template = 'ptah.manage:templates/intr-renderer.pt'


@intr_renderer('ptah:aclmap')
class ACLMapRenderer(Renderer):
    """ ACL map registration """

    title = 'ACL Maps'
    template = 'ptah.manage:templates/intr-aclmap.pt'


@intr_renderer('ptah:authchecker')
class AuthCheckerRenderer(Renderer):
    """ List of registered authentication checkers """

    title = 'Authentication checkers'
    template = 'ptah.manage:templates/intr-authchecker.pt'


@intr_renderer('ptah:authprovider')
class AuthProviderRenderer(Renderer):
    """ List of registered authentication providers """

    title = 'Authentication providers'
    template = 'ptah.manage:templates/intr-authprovider.pt'


@intr_renderer('ptah:settings-group')
class SettingsGroupRenderer(Renderer):
    """ List of registered settings groups """

    title = 'Settings'
    template = 'ptah.manage:templates/intr-settings.pt'


@intr_renderer('ptah.form:field')
class FieldRenderer(Renderer):
    """ List of registered fields """

    title = 'Fields'
    template = 'ptah.manage:templates/intr-field.pt'

    def __init__(self, request):
        super(FieldRenderer, self).__init__(request)

        self.previews = config.get_cfg_storage(PREVIEW_ID)


@intr_renderer('ptah:uiaction')
class uiActionRenderer(Renderer):
    """ List of registered ui actions """

    title = 'UI Actions'
    template = 'ptah.manage:templates/intr-uiaction.pt'


@intr_renderer('ptah:token-type')
class TokenTypeRenderer(Renderer):
    """ List of registered token types """

    title = 'Token types'
    template = 'ptah.manage:templates/intr-tokentype.pt'


@manage.intr_renderer('ptah.cms:type')
class ContentTypeRenderer(Renderer):
    """ Ptah content types """

    title = 'Content Types'
    template = 'ptah.manage:templates/intr-contenttype.pt'


@manage.intr_renderer('ptah:formatter')
class formatterRenderer(Renderer):
    """ List of formatters """

    title = 'Formatters'
    template = 'ptah.manage:templates/intr-formatter.pt'
