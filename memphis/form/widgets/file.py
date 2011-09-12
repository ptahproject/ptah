"""File widget implementation"""
import colander
from zope import interface
from memphis import view
from memphis.form import widget

from text import TextWidget
from interfaces import _, IFileWidget


class FileWidget(TextWidget):
    __doc__ = _(u'HTML File input widget')

    interface.implementsOnly(IFileWidget)

    widget('file', _(u'File widget'))

    klass = u'input-file'

    def deserialize(self, value):
        if hasattr(value, 'file'):
            data = {}
            data['fp'] = value.file
            data['filename'] = value.filename
            data['mimetype'] = value.type
            data['size'] = value.length
            return data
        else:
            if self.node.missing is colander.required:
                raise colander.Invalid(self, _('Required'))

            return self.node.missing


view.registerPagelet(
    'form-display', IFileWidget,
    template=view.template("memphis.form.widgets:file_display.pt"))

view.registerPagelet(
    'form-input', IFileWidget,
    template=view.template("memphis.form.widgets:file_input.pt"))
