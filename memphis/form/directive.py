""" widget directive implementation """
import colander
from memphis import view, config
from zope.interface import providedBy, implementedBy
from zope.interface.adapter import AdapterRegistry

from interfaces import IWidget


def widget(name, title='', layer=''):
    info = config.DirectiveInfo(allowed_scope=('class',))

    discriminator = ('memphis.form:widget', name, layer)

    info.attach(
        config.ClassAction(
            view.LayerWrapper(registerWidgetImpl, discriminator),
            (name, title),
            discriminator = discriminator)
        )


def registerWidget(factory, name, title='', layer=''):
    info = config.DirectiveInfo()

    discriminator = ('memphis.form:widget', name, layer)

    info.attach(
        config.Action(
            view.LayerWrapper(registerWidgetImpl, discriminator),
            (factory, name, title),
            discriminator = discriminator)
        )


def registerDefaultWidget(typ, name):
    registry.register(
        map(implementedBy, (colander.SchemaNode, typ)), IWidget, '', name)


widgets = {}
registry = AdapterRegistry()


def registerWidgetImpl(factory, name, title):
    widgets[name] = factory


def getWidget(name):
    return widgets.get(name, None)


def getDefaultWidget(node):
    name = registry.lookup(
        map(providedBy, (node, node.typ)), IWidget, default=None)
    if name is not None:
        return widgets[name]


def getDefaultWidgetName(node):
    return registry.lookup(
        map(providedBy, (node, node.typ)), IWidget, default=None)
