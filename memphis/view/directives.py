""" directives """
from pyramid.interfaces import IRequest

from memphis import config
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

    def initargs(name='', context=None, template=None, route=None, 
                 layout='', permission='__no_permission_required__',
                 default=False, decorator=None):
        return name, context, route, template, \
            layout, permission, default, decorator

    name, context, route, template, \
        layout, permission, default, decorator = initargs(*args, **kw)

    if info.scope in ('module', 'function call'): # function decorator
        def wrapper(factory):
            info.attach(
                config.Action(
                    registerViewImpl,
                    (factory, name, context, template,
                     route, layout, permission, default, decorator),
                    discriminator = ('memphis.view:view',name,context,route))
                )
            return factory
        return wrapper
    else:                     # class decorator
        info.attach(
            config.ClassAction(
                registerViewImpl,
                (name, context, template,
                 route, layout, permission, default, decorator),
                discriminator = ('memphis.view:view', name, context, route))
            )


def layout(name='',context=None,view=None,parent='',route=None,template=None):
    info = config.DirectiveInfo(allowed_scope=('class',))
    info.attach(
        config.ClassAction(
            registerLayoutImpl,
            (name, context, view, template, parent, route),
            discriminator = (
                'memphis.view:layout', name, context, view, route))
        )
