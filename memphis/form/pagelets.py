from zope import interface
from memphis import view
from memphis.form.interfaces import IForm, IInputForm, IDisplayForm, IWidget
from memphis.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE


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
    """ display widget view """
    view.pageletType('form-display-widget', IWidget)


class IWidgetInputView(INPUT_MODE):
    """ input widget renderer """
    view.pageletType('form-widget-input', IWidget)


class IWidgetDisplayView(DISPLAY_MODE):
    """ display widget renderer """
    view.pageletType('form-widget-display', IWidget)


class IWidgetHiddenView(HIDDEN_MODE):
    """ hidden widget renderer """
    view.pageletType('form-widget-hidden', IWidget)


view.registerPagelet(
    IFormView, IInputForm,
    template = view.template('memphis.form:templates/form.pt'))


view.registerPagelet(
    IFormView, IDisplayForm,
    template = view.template('memphis.form:templates/displayform.pt'))


view.registerPagelet(
    IFormActionsView, IInputForm,
    template = view.template('memphis.form:templates/form-actions.pt'))


view.registerPagelet(
    IFormWidgetView, IWidget,
    template = view.template('memphis.form:templates/widget.pt'))


view.registerPagelet(
    IFormDisplayWidgetView, IWidget,
    template = view.template('memphis.form:templates/widget-display.pt'))


view.static(
    'tiny_mce', 'memphis.form:static/tiny_mce')


view.library(
    "tiny_mce",
    resource="tiny_mce",
    path=('tiny_mce.js', 'jquery.tinymce.js'),
    type="js",
    require='jquery')
