""" directives """
import inspect
from pyramid.interfaces import IRequest

from memphis import config
from memphis.view.customize import LayerWrapper
from memphis.view.view import unset, registerViewImpl
from memphis.view.layout import registerLayoutImpl
from memphis.view.pagelet import registerPageletImpl


def pagelet(pageletType, context=None, template=None, layer=''):
    info = config.DirectiveInfo(allowed_scope=('class',))

    # register view in layer
    discriminator = ('memphis.view:pagelet', pageletType, context, layer)

    info.attach(
        config.ClassAction(
            LayerWrapper(registerPageletImpl, discriminator),
            (pageletType, context, template),
            discriminator = discriminator)
        )


def pyramidView(name=u'', context=None, route=None,
                template=None, layout=unset,
                permission='__no_permission_required__', layer=''):

    info = config.DirectiveInfo(
        allowed_scope=('class', 'module', 'function call'))

    discriminator = ('memphis.view:view', name, context, route, layer)

    if info.scope in ('module', 'function call'): # function decorator
        def wrapper(factory):
            info.attach(
                config.Action(
                    LayerWrapper(registerViewImpl, discriminator),
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
                LayerWrapper(registerViewImpl, discriminator),
                (name, context, template, route, layout, permission),
                discriminator = discriminator)
            )


def layout(name='',context=None,parent='',route=None,template=None,layer=''):
    info = config.DirectiveInfo(allowed_scope=('class',))

    discriminator = ('memphis.view:layout', name, context, route, layer)

    info.attach(
        config.ClassAction(
            LayerWrapper(registerLayoutImpl, discriminator),
            (name, context, template, parent, route),
            discriminator = discriminator)
        )
