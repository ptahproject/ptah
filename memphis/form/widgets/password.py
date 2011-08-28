"""Password widget implementation"""
import colander
from zope import interface
from memphis import config, view
from memphis.form import pagelets
from memphis.form.widgets import text

from interfaces import _, IPasswordWidget


class PasswordWidget(text.TextWidget):
    """Input type password widget implementation."""
    interface.implementsOnly(IPasswordWidget)
    config.adapts(colander.SchemaNode, colander.Str, name='password')

    klass = u'password-widget'

    __fname__ = 'password'
    __title__ = _('Password Widget')
    __description__ = _('HTML Password input widget.')


view.registerPagelet(
    'form-display', IPasswordWidget,
    template=view.template("memphis.form.widgets:password_display.pt"))

view.registerPagelet(
    'form-input', IPasswordWidget,
    template=view.template("memphis.form.widgets:password_input.pt"))
