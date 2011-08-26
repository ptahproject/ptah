""" directives """
import inspect
from pyramid.interfaces import IRequest

from memphis import config
from memphis.view.customize import layersManager
from memphis.view.view import registerViewImpl
from memphis.view.layout import registerLayoutImpl
from memphis.view.pagelet import registerPageletImpl, registerPageletTypeImpl


def pagelet(pageletType, context=None, template=None, layer=''):
    info = config.DirectiveInfo(allowed_scope=('class',))

    # register view in layer
    discriminator = ('memphis.view:pagelet', pageletType, context)
    layersManager.register(layer, discriminator)

    info.attach(
        config.ClassAction(
            registerPageletImpl, 
            (pageletType, context, template, layer, discriminator),
            discriminator = discriminator + (layer,))
        )


def pageletType(name, context=None):
    info = config.DirectiveInfo(allowed_scope=('class',))

    info.attach(
        config.ClassAction(
            registerPageletTypeImpl, (name, context),
            discriminator = ('memphis.view:pageletType', name, context),
            order = 1)
        )


def pyramidView(name='', context=None, template=None, route=None, 
                layout='', permission='__no_permission_required__',
                default=False, decorator=None, layer=''):

    info = config.DirectiveInfo(
        allowed_scope=('class', 'module', 'function call'))

    # register view in layer
    discriminator = ('memphis.view:view', name, context, route)
    layersManager.register(layer, discriminator)

    if info.scope in ('module', 'function call'): # function decorator
        def wrapper(factory):
            info.attach(
                config.Action(
                    registerViewImpl,
                    (factory, name, context, template, route, layout, 
                     permission, default, decorator, layer, discriminator),
                    discriminator = discriminator+(layer,))
                )
            return factory
        return wrapper
    else:                     # class decorator
        info.attach(
            config.ClassAction(
                registerViewImpl,
                (name, context, template, route, layout, 
                 permission, default, decorator, layer, discriminator),
                discriminator = discriminator+(layer,))
            )


def layout(name='', context=None, view=None, parent='',
           route=None, template=None, layer=''):
    info = config.DirectiveInfo(allowed_scope=('class',))

    # register view in layer
    discriminator = ('memphis.view:layout', name, context, view, route)
    layersManager.register(layer, discriminator)

    info.attach(
        config.ClassAction(
            registerLayoutImpl,
            (name, context, view, template, parent, route, layer, discriminator),
            discriminator = discriminator + (layer,))
        )
