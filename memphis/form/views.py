"""

$Id: views.py 11797 2011-01-31 04:13:41Z fafhrd91 $
"""
from memphis import config, view
from memphis.form import interfaces, pagelets


config.action(
    view.registerPagelet,
    pagelets.IFormView, interfaces.IInputForm,
    template = view.template('memphis.form:templates/form.pt'))

config.action(
    view.registerPagelet,
    pagelets.IFormView, interfaces.IEditForm,
    template = view.template('memphis.form:templates/editform.pt'))

config.action(
    view.registerPagelet,
    pagelets.IFormView, interfaces.ISubForm,
    template = view.template('memphis.form:templates/subform.pt'))


config.action(
    view.registerPagelet,
    pagelets.IFormActionsView, interfaces.IInputForm,
    template = view.template('memphis.form:templates/formactions.pt'))


config.action(
    view.registerPagelet,
    pagelets.IFormWidgetView, interfaces.IWidget,
    template = view.template('memphis.form:templates/widget.pt'))


config.action(
    view.registerPagelet,
    pagelets.IErrorViewSnippetView,
    template = view.template("memphis.form:templates/error.pt"))
