""" snippet implementation """
import logging
from zope.interface import implementer, Interface
from pyramid.httpexceptions import HTTPNotFound

from ptah import config
from ptah.view.base import View
from ptah.view.interfaces import ISnippet

log = logging.getLogger('ptah.view')

STYPE_ID = 'ptah.view:snippettype'
SNIPPET_ID = 'ptah.view:snippet'


@implementer(ISnippet)
class Snippet(View):
    """ Snippet implementation """

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
    """ Snippet type """

    def __init__(self, name, context, title, description):
        self.name = name
        self.context = context
        self.title = title
        self.description = description


def render_snippet(stype, context, request):
    snippet = request.registry.queryMultiAdapter(
        (context, request), ISnippet, stype)
    if snippet is None:
        raise HTTPNotFound()

    try:
        return snippet()
    except Exception as e:
        log.exception(str(e))
        raise


def snippettype(name, context=None, title='', description=''):
    stype = SnippetType(name, context, title, description)

    discr = (STYPE_ID, name)
    intr = config.Introspectable(SNIPPET_ID, discr, name, SNIPPET_ID)
    intr['name'] = name
    intr['context'] = context
    intr['title'] = title
    intr['description'] = description
    intr['stype'] = stype

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            lambda config, name, stype: \
                config.get_cfg_storage(STYPE_ID).update({name: stype}),
            (name, stype,),
            discriminator=discr, introspectables=(intr,), order = -1))


def snippet(name, context=None, template=None, layer=''):
    info = config.DirectiveInfo(allowed_scope=('class',))

    discr = (SNIPPET_ID, name, context, layer)

    intr = config.Introspectable(SNIPPET_ID, discr, name, SNIPPET_ID)
    intr['name'] = name
    intr['context'] = context
    intr['templates'] = template
    intr['layer'] = layer

    info.attach(
        config.ClassAction(
            config.LayerWrapper(register_snippet_impl, discr),
            (name, context, template, intr),
            discriminator=discr, introspectables=(intr,))
        )


def register_snippet(name, context=None, klass=None, template=None, layer=''):
    info = config.DirectiveInfo()
    discr = (SNIPPET_ID, name, context, layer)

    intr = config.Introspectable(SNIPPET_ID, discr, name, SNIPPET_ID)
    intr['name'] = name
    intr['context'] = context
    intr['templates'] = template
    intr['layer'] = layer

    info.attach(
        config.Action(
            config.LayerWrapper(register_snippet_impl, discr),
            (klass, name, context, template, intr),
            discriminator=discr, introspectables=(intr,))
        )


def register_snippet_impl(cfg, klass, stype, context, template, intr):
    cdict = {}
    if template is not None:
        cdict['template'] = template

    # find SnippetType info
    if stype not in cfg.get_cfg_storage(STYPE_ID):
        log.warning("Can't find SnippetType %s", stype)

    requires = [context, Interface]

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

    intr['class'] = snippet_class

    # register snippet
    cfg.registry.registerAdapter(
        snippet_class, requires, ISnippet, name = stype)
