""" introspector renderers """
import sys
import inspect

import ptah
from ptah import config, view, manage, form
from ptah.manage import intr_renderer, get_manage_url
from ptah.manage.manage import INTROSPECT_ID


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
    """ zca event declarations """

    title = 'Events'
    template = view.template('ptah.manage:templates/intr-event.pt')


@intr_renderer('ptah.config:adapter')
class AdapterDirective(object):
    """ zc adapter registrations """

    title = 'zc adapters'
    actions = view.template('ptah.manage:templates/directive-adapter.pt')

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
    template = view.template('ptah.manage:templates/intr-snippettype.pt')


@intr_renderer('ptah.view:route')
class RouteDirective(Renderer):
    """ pyramid routes """

    title = 'Routes'
    actions = view.template('ptah.manage:templates/directive-route.pt')

    def renderActions(self, *actions):
        return self.actions(
            actions = actions,
            manage = get_manage_url(self.request),
            request = self.request)


@intr_renderer('ptah.config:subscriber')
class SubscriberRenderer(Renderer):
    """ zca event subscribers """

    title = 'Event subscribers'
    template = view.template('ptah.manage:templates/intr-subscriber.pt')

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
    """ pyramid views """

    title = 'Views'
    actions = view.template('ptah.manage:templates/directive-view.pt')

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
            factory,name,context,template,route,layout,permission,intr=action.args

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
    template = view.template('ptah.manage:templates/intr-permission.pt')


@intr_renderer('ptah:role')
class RoleIntrospection(Renderer):
    """ Role registrations """

    title = 'Role'
    template = view.template('ptah.manage:templates/intr-role.pt')


@intr_renderer('ptah:resolver')
class UriRenderer(Renderer):
    """ Uri resolvers """

    title = 'Uri resolver'
    template = view.template('ptah.manage:templates/intr-uriresolver.pt')
