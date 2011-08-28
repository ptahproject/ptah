"""Button widget implementation"""
import zope.interface

from memphis import view
from memphis.form import interfaces, pagelets
from memphis.form.widget import Widget
from memphis.form.widgets import widget
from memphis.form import AC_PRIMARY, AC_DANGER, AC_SUCCESS, AC_INFO

from interfaces import IButtonWidget


class ButtonWidget(widget.HTMLInputWidget, Widget):
    """A simple button of a form."""
    zope.interface.implementsOnly(IButtonWidget)

    klass = u'btn button-widget'

    def update(self):
        self.value = self.node.title
        if self.node.actype == AC_PRIMARY:
            self.addClass('primary')
        elif self.node.actype == AC_DANGER:
            self.addClass('danger')
        elif self.node.actype == AC_SUCCESS:
            self.addClass('success')
        elif self.node.actype == AC_INFO:
            self.addClass('info')


view.registerPagelet(
    'form-display', IButtonWidget,
    template=view.template("memphis.form.widgets:button_display.pt"))

view.registerPagelet(
    'form-input', IButtonWidget,
    template=view.template("memphis.form.widgets:button_input.pt"))
