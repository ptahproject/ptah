""" directives """
import sys, inspect
import zope.component
from martian.directive import Directive
from martian.error import GrokImportError
from martian import CLASS, MODULE, ONCE_NOBASE, MULTIPLE_NOBASE


def getInfo(level=3):
    frame = inspect.stack()[level][0]
    info = ''
    try:
        tb = inspect.getframeinfo(frame)
        if tb.code_context:
            info = ' File "%s", line %d, in %s\n' \
                '      %s'% (tb.filename, tb.lineno,
                             tb.function, tb.code_context[0])
    finally:
        del frame
    return info


def getModule(frame):
    if frame.f_locals is frame.f_globals:
        return frame.f_locals

    if 'self' in frame.f_locals:
        mod = frame.f_locals['self'].__module__
        if mod in sys.modules:
            return sys.modules[mod].__dict__


class action(Directive):
    scope = MODULE
    store = MULTIPLE_NOBASE

    # for tests only
    immediately = False

    def __init__(self, *args, **kw):
        self.name = self.__class__.__name__

        if '__frame' in kw:
            self.frame = frame = kw.pop('__frame')
        else:
            self.frame = frame = sys._getframe(1)

        _locals = None

        if type(frame) is dict:
            _locals = frame
        else:
            if not self.scope.check(frame):
                _locals = getModule(frame)
                if _locals is None:
                    raise GrokImportError(
                        "The '%s' directive can only be used on %s level." %
                        (self.name, self.scope.description))
            else:
                _locals = frame.f_locals

        self.check_factory_signature(*args, **kw)

        value = self.factory(*args, **kw)
        if self.immediately:
            for key in ('__order', '__discriminator'):
                if key in value[2]:
                    del value[2][key]
            value[0](*value[1], **value[2])
        else:
            self.store.set(_locals, self, value)

    def factory(self, callable, *args, **kw):
        if '__info' in kw:
            info = kw.pop('__info')
        else:
            info = getInfo()
        return callable, args, kw, info


class registerIn(Directive):
    scope = MODULE
    store = ONCE_NOBASE

    def factory(self, name):
        return name, getInfo()


class adapts(Directive):
    scope = CLASS
    store = MULTIPLE_NOBASE

    def factory(self, *args, **kw):
        name = kw.get('name', '')
        required = []
        for val in args:
            if isinstance(val, basestring):
                name = val
            else:
                required.append(val)
        return tuple(required), name, getInfo()


class utility(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    def factory(self, provides, name=''):
        return provides, name, getInfo()


class adapter(zope.component.adapter):

    def __init__(self, *args, **kwargs):
        zope.component.adapter.__init__(self, *args)
        self.required = args
        self.kwargs = kwargs

    def __call__(self, ob):
        ob = zope.component.adapter.__call__(self, ob)

        if not hasattr(ob, '_register_adapter'):
            ob._register_adapter = []

        ob._register_adapter.append((self.required, self.kwargs, getInfo(2)))
        return ob


class handler:

    def __init__(self, *required):
        self.required = required

    def __call__(self, ob):
        if not hasattr(ob, '_register_handler'):
            ob._register_handler = []

        ob._register_handler.append((self.required, getInfo(2)))
        return ob
