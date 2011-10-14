""" snippet implementation """
import sys, logging
from zope import interface
from pyramid.httpexceptions import HTTPNotFound

from memphis import config
from memphis.view.base import View
from memphis.view.customize import LayerWrapper
from memphis.view.interfaces import ISnippet

log = logging.getLogger('memphis.view')

stypes = {}


class Snippet(View):
    interface.implements(ISnippet)

    template = None
    _params = None

    def render(self):
        kwargs = self._params or {}
        kwargs.update({'view': self,
                       'context': self.context,
                       'request': self.request})

        return self.template(**kwargs)

    def __call__(self, *args, **kw):
        self._params = self.update()
        return self.render()


class SnippetType(object):

    def __init__(self, name, context, title, description):
        self.name = name
        self.context = context
        self.title = title
        self.description = description


def render_snippet(stype, context, request):
    snippet = config.registry.queryMultiAdapter(
        (context, request), ISnippet, stype)
    if snippet is None:
        raise HTTPNotFound

    try:
        return snippet()
    except Exception, e:
        log.exception(str(e))
        raise


def snippettype(name, context=None, title='', description=''):
    stype = SnippetType(name, context, title, description)
    stypes[name] = stype

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            lambda name, stype: stypes.update({name: stype}),
            (name, stype,),
            discriminator = ('memphis.view:snippettype', name),
            order = 1))


def register_snippet(name, context=None, klass=None, template=None, layer=''):
    info = config.DirectiveInfo()

    discriminator = ('memphis.view:snippet', name, context, layer)

    info.attach(
        config.Action(
            LayerWrapper(register_snippet_impl, discriminator),
            (klass, name, context, template),
            discriminator = discriminator)
        )


def register_snippet_impl(klass, stype, context, template):
    cdict = {}
    if template is not None:
        cdict['template'] = template

    # find SnippetType info
    if stype not in stypes:
        log.warning("Can't find SnippetType %s", stype)

    requires = [context, interface.Interface]

    # Build a new class
    if klass is not None and issubclass(klass, Snippet):
        snippet_class = klass
        for attr, value in cdict.items():
            setattr(snippet_class, attr, value)
    else:
        # Build a new class
        if klass is None:
            bases = (Snippet,)
        else:
            bases = (klass, Snippet)

        snippet_class = type('Snippet %s'%klass, bases, cdict)

    # register snippet
    config.registry.registerAdapter(
        snippet_class, requires, ISnippet, name = stype)
