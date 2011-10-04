from zope import interface
from memphis import view
from memphis.form.field import Field
from memphis.form.interfaces import IForm, IInputForm, IDisplayForm, IWidget

FORM_VIEW = 'form-view'
FORM_ACTIONS = 'form-actions'
FORM_WIDGET = 'form-widget'
FORM_DISPLAY_WIDGET = 'form-display-widget'

view.pageletType(FORM_VIEW, IForm, 'Form view')
view.pageletType(FORM_ACTIONS, IForm, 'Form actions')
view.pageletType(FORM_WIDGET, Field, 'Form widget')
view.pageletType(FORM_DISPLAY_WIDGET, Field, 'Form display widget')


view.registerPagelet(
    'form-view', IInputForm,
    template = view.template('memphis.form:templates/form.pt'))


view.registerPagelet(
    'form-view', IDisplayForm,
    template = view.template('memphis.form:templates/displayform.pt'))


view.registerPagelet(
    'form-actions', IInputForm,
    template = view.template('memphis.form:templates/form-actions.pt'))


view.registerPagelet(
    'form-widget', Field,
    template = view.template('memphis.form:templates/widget.pt'))


view.registerPagelet(
    'form-display-widget', Field,
    template = view.template('memphis.form:templates/widget-display.pt'))


view.static(
    'tiny_mce', 'memphis.form:static/tiny_mce')


view.library(
    "tiny_mce",
    resource="tiny_mce",
    path=('tiny_mce.js', 'jquery.tinymce.js'),
    type="js",
    require='jquery')
