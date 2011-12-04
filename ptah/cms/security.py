import inspect
from pyramid.compat import string_types

import ptah
from ptah import config
from ptah.cms.permissions import View
from ptah.cms.interfaces import NotFound, Forbidden


def wrap(content):
    if isinstance(content, string_types):
        content = ptah.cms.load(content)
    else:
        ptah.cms.load_parents(content)

    if content is None:
        raise NotFound()

    return NodeWrapper(content)


class NodeWrapper(object):

    def __init__(self, content):
        self._content = content
        self._actions = getattr(content, '__ptahcms_actions__', None)

    def __getattr__(self, action):
        if not self._actions or action not in self._actions:
            raise NotFound(action)

        fname, permission = self._actions[action]
        if permission:
            if not ptah.check_permission(permission, self._content):
                raise Forbidden(action)

        return ActionWrapper(self._content, fname)


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


def build_class_actions(cls):
    actions = cls.__dict__.get('__ptahcms_actions__', None)
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
