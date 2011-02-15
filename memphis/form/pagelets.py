from zope import interface
from memphis import view
from memphis.form.interfaces import IForm, IWidget, IErrorViewSnippet


class IFormView(interface.Interface):
    """ pagelet type """
    view.pageletType('form-view', IForm)


class IFormActionsView(interface.Interface):
    """ form actions view """
    view.pageletType('form-actions', IForm)


class IFormWidgetView(interface.Interface):
    """ widget view """
    view.pageletType('form-widget', IWidget)


class IWidgetInputView(interface.Interface):
    """ pagelet type """
    view.pageletType('form-widget-input', IWidget)


class IWidgetDisplayView(interface.Interface):
    """ pagelet type """
    view.pageletType('form-widget-display', IWidget)


class IWidgetHiddenView(interface.Interface):
    """ pagelet type """
    view.pageletType('form-widget-hidden', IWidget)


class IErrorViewSnippetView(interface.Interface):
    """ error view pagelet """
    view.pageletType('form-error-view', IErrorViewSnippet)
