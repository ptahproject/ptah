""" directives """
from ptah import config
from ptah.view.customize import LayerWrapper
from ptah.view.view import unset, register_view_impl
from ptah.view.layout import register_layout_impl
from ptah.view.snippet import register_snippet_impl


def snippet(name, context=None, template=None, layer=''):
    info = config.DirectiveInfo(allowed_scope=('class',))

    discriminator = ('ptah.view:snippet', name, context, layer)

    info.attach(
        config.ClassAction(
            LayerWrapper(register_snippet_impl, discriminator),
            (name, context, template),
            discriminator = discriminator)
        )


def pview(name=u'', context=None, route=None,
          template=None, layout=unset,
          permission='__no_permission_required__', layer=''):

    info = config.DirectiveInfo(
        allowed_scope=('class', 'module', 'function call'))

    discriminator = ('ptah.view:view', name, context, route, layer)

    if info.scope in ('module', 'function call'): # function decorator
        def wrapper(factory):
            info.attach(
                config.Action(
                    LayerWrapper(register_view_impl, discriminator),
                    (factory, name, context, template, route,
                     layout, permission),
                    discriminator = discriminator)
                )
            return factory
        return wrapper
    else:
        # class decorator
        info.attach(
            config.ClassAction(
                LayerWrapper(register_view_impl, discriminator),
                (name, context, template, route, layout, permission),
                discriminator = discriminator)
            )


def layout(name='', context=None, parent='', route=None,template=None,layer=''):
    info = config.DirectiveInfo(allowed_scope=('class',))

    discriminator = ('ptah.view:layout', name, context, route, layer)

    info.attach(
        config.ClassAction(
            LayerWrapper(register_layout_impl, discriminator),
            (name, context, template, parent, route),
            discriminator = discriminator)
        )
