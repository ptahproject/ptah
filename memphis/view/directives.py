""" directives """
from pyramid.interfaces import IRequest

from memphis import config
from memphis.view.interfaces import INavigationRoot
from memphis.view.view import registerViewImpl
from memphis.view.layout import registerLayoutImpl
from memphis.view.pagelet import registerPageletImpl, registerPageletTypeImpl


def pagelet(pageletType, context=None, template=None, layer=None):
    info = config.DirectiveInfo(allowed_scope=('class',))

    info.attach(
        config.ClassAction(
            registerPageletImpl, (pageletType, context, template, layer),
            discriminator=('memphis.view:pagelet', pageletType,context,layer))
        )


def pageletType(name, context=None):
    info = config.DirectiveInfo(allowed_scope=('class',))

    info.attach(
        config.ClassAction(
            registerPageletTypeImpl, (name, context),
            discriminator = ('memphis.view:pageletType', name, context))
        )


def pyramidView(*args, **kw):
    info = config.DirectiveInfo(
        allowed_scope=('class', 'module', 'function call'))

    def initargs(name='', context=None, template=None, route_name=None, 
                 layout='', permission='__no_permission_required__',
                 default=False, decorator=None):
        return name, context, route_name, template, \
            layout, permission, default, decorator

    name, context, route_name, template, \
        layout, permission, default, decorator = initargs(*args, **kw)

    if info.scope in ('module', 'function call'): # function decorator
        def wrapper(factory):
            info.attach(
                config.Action(
                    registerViewImpl,
                    (factory, name, context, template,
                     route_name, layout, permission, default, decorator),
                    discriminator = (
                        'memphis.view:view', name, context, route_name))
                )
            return factory
        return wrapper
    else:                     # class decorator
        info.attach(
            config.ClassAction(
                registerViewImpl,
                (name, context, template,
                 route_name, layout, permission, default, decorator),
                discriminator = (
                    'memphis.view:view', name, context, route_name))
            )


def layout(*args, **kw):
    info = config.DirectiveInfo(allowed_scope=('class',))

    def initargs(name='', context=INavigationRoot, 
                 view=None, parent='', route_name=None):
        return name, context, view, parent, route_name

    name, context, view, parent, route_name = initargs(*args, **kw)

    info.attach(
        config.ClassAction(
            registerLayoutImpl,
            (name, context, view, None, parent, route_name),
            discriminator = (
                'memphis.view:layout', name, context, view, route_name))
        )
