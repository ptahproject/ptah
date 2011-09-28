import ptah
import inspect
from memphis import config
from zope.interface import providedBy, Interface, implements

from node import loadNode, loadParents
from permissions import View
from interfaces import NotFound, Forbidden


def cms(content):
    if isinstance(content, basestring):
        content = loadNode(content)
    else:
        loadParents(content)

    if content is None:
        raise NotFound()

    return NodeWrapper(content)


class NodeWrapper(object):

    def __init__(self, content):
        self.content = content
        self.actions = getattr(content, '__ptahcms_actions__', None)

    def __getattr__(self, action):
        if not self.actions or action not in self.actions:
            raise NotFound(action)

        permission = self.actions[action]
        if permission:
            if not ptah.checkPermission(permission, self.content, throw=False):
                raise Forbidden(key)

        return ActionWrapper(self.content, action)


class ActionWrapper(object):

    def __init__(self, content, action):
        self.content = content
        self.action = action

    def __call__(self, *args, **kw):
        return getattr(self.content, self.action)(*args, **kw)


def action(func=None, permission = View):
    info = config.DirectiveInfo(allowed_scope=('class',))

    def wrapper(func):
        info.attach(
            config.ClassAction(
                actionImpl, (func, permission),
                discriminator = ('ptah-cms:action', func))
            )

        return func

    if func is not None:
        return wrapper(func)
    return wrapper


def actionImpl(cls, func, permission):
    actions = getattr(cls, '__ptahcms_actions__', None)
    if actions is None:
        # get actions from parents
        mro = inspect.getmro(cls)

        actions = {}
        for idx in range(len(mro)-1, 0, -1):
            a = getattr(mro[idx], '__ptahcms_actions__', None)
            if a is not None:
                actions.update(a)

        cls.__ptahcms_actions__ = actions

    actions[func.__name__] = permission
