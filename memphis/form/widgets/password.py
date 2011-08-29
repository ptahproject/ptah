"""Password widget implementation"""
from zope import interface
from memphis import view
from memphis.form import pagelets, widget
from memphis.form.widgets import text

from interfaces import _, IPasswordWidget


class PasswordWidget(text.TextWidget):
    __doc__ = _('HTML Password input widget.')

    widget('password', _('Password Widget'))
    interface.implementsOnly(IPasswordWidget)

    klass = u'password-widget'


view.registerPagelet(
    'form-display', IPasswordWidget,
    template=view.template("memphis.form.widgets:password_display.pt"))

view.registerPagelet(
    'form-input', IPasswordWidget,
    template=view.template("memphis.form.widgets:password_input.pt"))
