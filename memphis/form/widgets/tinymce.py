""" TinyMCE widget """
from zope import interface
from memphis import view
from memphis.form import pagelets, widget

from textarea import TextAreaWidget
from interfaces import _, ITinymceWidget


class TinymceWidget(TextAreaWidget):
    __doc__ = _(u'TinyMCE Text Area input widget')

    widget('tinymce', _(u'TinyMCE widget'))
    interface.implements(ITinymceWidget)

    klass = u'tinymce-widget'

    width = '400px'
    height = '200px'
    theme = "advanced"


view.registerPagelet(
    'form-input', ITinymceWidget,
    template=view.template("memphis.form.widgets:tinymce_input.pt"))
