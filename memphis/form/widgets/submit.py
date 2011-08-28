"""Submit Widget Implementation"""
from zope import interface
from memphis import config, view
from memphis.form import interfaces, pagelets
from memphis.form.widgets import button

from interfaces import ISubmitWidget


class SubmitWidget(button.ButtonWidget):
    """A submit button of a form."""
    config.adapts(interfaces.IButton, None)
    interface.implementsOnly(ISubmitWidget)

    klass = u'btn submit-widget'


view.registerPagelet(
    'form-display', ISubmitWidget,
    template=view.template("memphis.form.widgets:submit_display.pt"))


view.registerPagelet(
    'form-input', ISubmitWidget,
    template=view.template("memphis.form.widgets:submit_input.pt"))
