""" ui actions """
import ptah
from memphis import config
from zope import interface


class IAction(interface.Interface):
    """ marker interface for actions """


class Action(object):
    interface.implements(IAction)

    id = ''
    title = ''
    description = ''
    action = ''
    actionFactory = None
    condition = None
    permission = None
    sortWeight = 1.0,
    data = None

    def __init__(self, id='', **kw):
        self.id = id
        self.__dict__.update(kw)

    def url(self, context, request, url=''):
        if self.actionFactory is not None:
            return self.actionFactory(context, request)

        if self.action.startswith('/'):
            return '%s%s'%(request.application_url, self.action)
        else:
            return '%s%s'%(url, self.action)

    def check(self, context, request):
        if self.permission:
            if not ptah.checkPermission(
                self.permission, context, request):
                return False

        if self.condition is not None:
            return self.condition(context, request)

        return True


def _contentAction(id, context, ac):
    config.registry.registerAdapter(ac, (context,), IAction, id)


def uiaction(context, id, title,
             description = '',
             action='', condition=None, permission=None,
             sortWeight = 1.0, **kw):

    kwargs = {'id': id,
              'title': title,
              'description': description,
              'condition': condition,
              'permission': permission,
              'sortWeight': sortWeight,
              'data': kw}

    if callable(action):
        kwargs['actionFactory'] = action
    else:
        kwargs['action'] = action

    ac = Action(**kwargs)
    info = config.DirectiveInfo()

    info.attach(
        config.Action(
            _contentAction, (id, context, ac,),
            discriminator = ('ptah-cms:ui-action', id, context))
        )


def list_uiactions(content, request):
    url = request.resource_url(content)

    actions = []
    for name, action in config.registry.adapters.lookupAll(
        (interface.providedBy(content),), IAction):
        if action.check(content, request):
            actions.append(
                (action.sortWeight,
                 {'id': action.id,
                  'url': action.url(content, request, url),
                  'title': action.title,
                  'description': action.description,
                  'data': action.data}))

    actions.sort()
    return [ac for _w, ac in actions]
