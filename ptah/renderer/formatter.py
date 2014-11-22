""" formatters """
from pyramid.registry import Introspectable

ID_FORMATTER = 'ptah.renderer:formatter'


def add_formatter(cfg, name, callable):
    discr = (ID_FORMATTER, name)

    intr = Introspectable(ID_FORMATTER, discr, name, 'ptah.renderer-formatter')
    intr['name'] = name
    intr['callable'] = callable
    intr['description'] = callable.__doc__

    def action():
        storage = cfg.registry.get(ID_FORMATTER)
        if storage is None:
            storage = cfg.registry[ID_FORMATTER] = {}

        storage[name] = callable

    cfg.action(discr, action, introspectables=(intr,))


class wrapper(object):

    def __init__(self, request, callable):
        self.request = request
        self.callable = callable

    def __call__(self, *args, **kw):
        return self.callable(self.request, *args, **kw)


class formatters(object):

    def __init__(self, request, default={}):
        self._request = request
        self._f = request.registry.get(ID_FORMATTER, default)
        self._wrappers = {}

    def __getitem__(self, name):
        if name in self._wrappers:
            return self._wrappers[name]

        wrp = self._wrappers[name] = wrapper(self._request, self._f[name])
        setattr(self, name, wrp)

        return wrp

    def __getattr__(self, name):
        if name in self._f:
            return self[name]

        raise AttributeError(name)
