"""Submit Widget Implementation"""
import zope.interface
from memphis import config, view
from memphis.form import interfaces, pagelets
from memphis.form.widgets import button


class SubmitWidget(button.ButtonWidget):
    """A submit button of a form."""
    config.adapts(interfaces.IButton, None, None)
    zope.interface.implementsOnly(interfaces.ISubmitWidget)

    klass = u'btn submit-widget'


view.registerPagelet(
    pagelets.IWidgetDisplayView, interfaces.ISubmitWidget,
    template=view.template("memphis.form.widgets:submit_display.pt"))


view.registerPagelet(
    pagelets.IWidgetInputView, interfaces.ISubmitWidget,
    template=view.template("memphis.form.widgets:submit_input.pt"))
