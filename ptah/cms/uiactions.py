""" ui actions """
import ptah
from ptah import config
from zope import interface


class IAction(interface.Interface):
    """ marker interface for actions """


class Action(object):
    interface.implements(IAction)

    id = ''
    title = ''
    description = ''
    action = ''
    action_factory = None
    condition = None
    permission = None
    sort_weight = 1.0,
    data = None

    def __init__(self, id='', **kw):
        self.id = id
        self.__dict__.update(kw)

    def url(self, context, request, url=''):
        if self.action_factory is not None:
            return self.action_factory(context, request)

        if self.action.startswith('/'):
            return '%s%s'%(request.application_url, self.action)
        else:
            return '%s%s'%(url, self.action)

    def check(self, context, request):
        if self.permission:
            if not ptah.check_permission(
                self.permission, context, request):
                return False

        if self.condition is not None:
            return self.condition(context, request)

        return True


def uiaction(context, id, title,
             description = '',
             action='', condition=None, permission=None,
             sort_weight = 1.0, **kw):

    kwargs = {'id': id,
              'title': title,
              'description': description,
              'condition': condition,
              'permission': permission,
              'sort_weight': sort_weight,
              'data': kw}

    if callable(action):
        kwargs['action_factory'] = action
    else:
        kwargs['action'] = action

    ac = Action(**kwargs)
    info = config.DirectiveInfo()

    info.attach(
        config.Action(
            lambda cfg, id, context, ac: \
                cfg.registry.registerAdapter(ac, (context,), IAction, id),
            (id, context, ac,),
            discriminator = ('ptah-cms:ui-action', id, context))
        )


def list_uiactions(content, request):
    url = request.resource_url(content)

    actions = []
    for name, action in request.registry.adapters.lookupAll(
        (interface.providedBy(content),), IAction):
        if action.check(content, request):
            actions.append(
                (action.sort_weight,
                 {'id': action.id,
                  'url': action.url(content, request, url),
                  'title': action.title,
                  'description': action.description,
                  'data': action.data}))

    actions.sort()
    return [ac for _w, ac in actions]
