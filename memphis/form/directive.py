""" widget directive implementation """
from memphis import view, config
from interfaces import IWidget

widgets = {}

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


def registerWidgetImpl(factory, name, title):
    widgets[name] = factory


def getWidget(name):
    return widgets.get(name, None)
