import ptah
import inspect
from memphis import config
from zope.interface import providedBy, Interface, implements

import ptah_cms
from permissions import View
from interfaces import NotFound, Forbidden


def cms(content):
    if isinstance(content, basestring):
        content = ptah_cms.load(content)
    else:
        ptah_cms.loadParents(content)

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

        fname, permission = self.actions[action]
        if permission:
            if not ptah.checkPermission(permission, self.content, throw=False):
                raise Forbidden(action)

        return ActionWrapper(self.content, fname)


class ActionWrapper(object):

    def __init__(self, content, action):
        self.content = content
        self.action = action

    def __call__(self, *args, **kw):
        return getattr(self.content, self.action)(*args, **kw)


def action(func=None, name=None, permission = View):
    info = config.DirectiveInfo(allowed_scope=('class',))

    actions = info.locals.get('__ptahcms_actions__', None)
    if actions is None:
        actions = {}
        info.locals['__ptahcms_actions__'] = actions

    def wrapper(func, name=name):
        if name is None:
            name = func.__name__

        actions[name] = (func.__name__, permission)

        return func

    if func is not None:
        return wrapper(func)
    return wrapper


def buildClassActions(cls):
    actions = getattr(cls, '__ptahcms_actions__', None)
    if actions is None:
        actions = {}

    # get actions from parents
    mro = inspect.getmro(cls)

    for idx in range(len(mro)-1, 0, -1):
        a = getattr(mro[idx], '__ptahcms_actions__', None)
        if a is not None:
            for name, action in a.items():
                if name not in actions:
                    actions[name] = action

    cls.__ptahcms_actions__ = actions
