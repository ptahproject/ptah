""" form views """
from memphis import view
from memphis.form import interfaces, pagelets

view.static(
    'tiny_mce', 'memphis.form:static/tiny_mce')

view.library(
    "tiny_mce",
    resource="tiny_mce",
    path=('tiny_mce.js', 'jquery.tinymce.js'),
    type="js",
    require='jquery-ui')


view.registerPagelet(
    pagelets.IFormView, interfaces.IInputForm,
    template = view.template('memphis.form:templates/form.pt'))

view.registerPagelet(
    pagelets.IFormView, interfaces.IEditForm,
    template = view.template('memphis.form:templates/editform.pt'))

view.registerPagelet(
    pagelets.IFormView, interfaces.ISubForm,
    template = view.template('memphis.form:templates/subform.pt'))

view.registerPagelet(
    pagelets.IFormView, interfaces.IDisplayForm,
    template = view.template('memphis.form:templates/displayform.pt'))

view.registerPagelet(
    pagelets.IFormActionsView, interfaces.IInputForm,
    template = view.template('memphis.form:templates/formactions.pt'))

view.registerPagelet(
    pagelets.IFormWidgetView, interfaces.IWidget,
    template = view.template('memphis.form:templates/widget.pt'))

view.registerPagelet(
    pagelets.IFormDisplayWidgetView, interfaces.IWidget,
    template = view.template('memphis.form:templates/widget_display.pt'))

view.registerPagelet(
    pagelets.IErrorViewSnippetView,
    template = view.template("memphis.form:templates/error.pt"))
