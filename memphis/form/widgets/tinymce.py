""" TinyMCE widget """
from zope import interface
from memphis import view
from memphis.form import pagelets

from textarea import TextAreaWidget
from interfaces import _, ITinymceWidget


class TinymceWidget(TextAreaWidget):
    interface.implements(ITinymceWidget)

    klass = u'tinymce-widget'

    __fname__ = 'tinymce'
    __title__ = _(u'TinyMCE widget')
    __description__ = _(u'TinyMCE Text Area input widget')

    width = '400px'
    height = '200px'
    theme = "advanced"


view.registerPagelet(
    pagelets.IWidgetInputView, ITinymceWidget,
    template=view.template("memphis.form.widgets:tinymce_input.pt"))
