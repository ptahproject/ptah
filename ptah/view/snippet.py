""" snippet implementation """
import logging
from zope import interface
from pyramid.httpexceptions import HTTPNotFound

from ptah import config
from ptah.view.base import View
from ptah.view.customize import LayerWrapper
from ptah.view.interfaces import ISnippet

log = logging.getLogger('ptah.view')

STYPE_ID = 'ptah.view:snippettype'


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
    snippet = request.registry.queryMultiAdapter(
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

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            lambda config, name, stype: \
                config.get_cfg_storage(STYPE_ID).update({name: stype}),
            (name, stype,),
            discriminator = (STYPE_ID, name), order = 1))


def register_snippet(name, context=None, klass=None, template=None, layer=''):
    info = config.DirectiveInfo()

    discriminator = ('ptah.view:snippet', name, context, layer)

    info.attach(
        config.Action(
            LayerWrapper(register_snippet_impl, discriminator),
            (klass, name, context, template),
            discriminator = discriminator)
        )


def register_snippet_impl(cfg, klass, stype, context, template):
    cdict = {}
    if template is not None:
        cdict['template'] = template

    # find SnippetType info
    if stype not in cfg.get_cfg_storage(STYPE_ID):
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
    cfg.registry.registerAdapter(
        snippet_class, requires, ISnippet, name = stype)
