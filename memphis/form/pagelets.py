from zope import interface
from memphis import view
from memphis.form import interfaces
from memphis.form.interfaces import IForm, IWidget


class IFormView(interface.Interface):
    """ pagelet type """
    view.pageletType('form-view', IForm)


class IFormActionsView(interface.Interface):
    """ form actions view """
    view.pageletType('form-actions', IForm)


class IFormWidgetView(interface.Interface):
    """ widget view """
    view.pageletType('form-widget', IWidget)


class IFormDisplayWidgetView(interface.Interface):
    """ widget view """
    view.pageletType('form-display-widget', IWidget)


class IWidgetInputView(interfaces.INPUT_MODE):
    """ pagelet type """
    view.pageletType('form-widget-input', IWidget)


class IWidgetDisplayView(interfaces.DISPLAY_MODE):
    """ pagelet type """
    view.pageletType('form-widget-display', IWidget)


class IWidgetHiddenView(interfaces.HIDDEN_MODE):
    """ pagelet type """
    view.pageletType('form-widget-hidden', IWidget)
