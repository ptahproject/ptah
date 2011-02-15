""" directives """
import inspect
import zope.component
from martian.directive import Directive
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


class action(Directive):
    scope = MODULE
    store = MULTIPLE_NOBASE

    def factory(self, callable, *args, **kw):
        return callable, args, kw, getInfo()


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
