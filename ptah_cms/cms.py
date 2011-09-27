from memphis import config
from zope.interface import providedBy, Interface, implements

from node import loadNode
from interfaces import NotFound, Forbidden


def cms(content):
    if isinstance(content, basestring):
        content = loadNode(content)

    if content is None:
        raise NotFound()

    return CMS(content)


class CMS(object):

    def __init__(self, content):
        self.content = content
        self.provided = providedBy(content)

    def __getattr__(self, key):
        action = config.registry.adapters.lookup(
            (self.provided,), IAction, name=key, default=None)
        if action is None:
            raise NotFound(key)

        if action.permission:
            if not ptah.checkPermission(
                action.permission, content, throw=False):
                raise Forbidden(key)

        return ActionWrapper(self.content, action.action)


class ActionWrapper(object):

    def __init__(self, content, action):
        self.content = content
        self.action = action

    def __call__(self, *args, **kw):
        return self.action(self.content, *args, **kw)


class IAction(Interface):
    pass


class Action(object):
    implements(IAction)

    id = ''
    title = ''
    description = ''
    action = ''
    permission = None

    def __init__(self, id, action, title, description, permission):
        self.id = id
        self.action = action
        self.title = title
        self.description = description 
        self.permission = permission


def action(id, context, permission = None, title = '', description = ''):
    info = config.DirectiveInfo()

    def wrapper(func):
        def actionImpl(func, id, context, permission, title, description):
            ac = Action(id, func, permission, title, description)
            config.registry.registerAdapter(ac, (context,), IAction, id)

        info.attach(
            config.Action(
                actionImpl, (func, id, context, permission, title, description),
                discriminator = ('ptah-cms:action', id, context))
            )

        return func

    return wrapper


def registerAction(id, callable, context,
                   permission=None, title='', description=''):
    info = config.DirectiveInfo()

    ac = Action(id, callable, permission, title, description)

    def _register(id, context, ac):
        config.registry.registerAdapter(ac, (context,), IAction, id)

    info.attach(
        config.Action(
            _register, (id, context, ac),
            discriminator = ('ptah-cms:action', id, context))
        )
