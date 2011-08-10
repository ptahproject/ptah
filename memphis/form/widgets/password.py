"""Password Widget Implementation"""
import colander
from zope import interface
from memphis import config, view
from memphis.form import pagelets
from memphis.form.widgets import text
from memphis.form.interfaces import _, IPasswordWidget


class PasswordWidget(text.TextWidget):
    """Input type password widget implementation."""
    interface.implementsOnly(IPasswordWidget)
    config.adapts(colander.SchemaNode, colander.Str, None, name='password')

    klass = u'password-widget'

    __fname__ = 'password'
    __title__ = _('Password Widget')
    __description__ = _('HTML Password input widget.')


view.registerPagelet(
    pagelets.IWidgetDisplayView, IPasswordWidget,
    template=view.template("memphis.form.widgets:password_display.pt"))

view.registerPagelet(
    pagelets.IWidgetInputView, IPasswordWidget,
    template=view.template("memphis.form.widgets:password_input.pt"))
