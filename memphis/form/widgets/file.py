"""File Widget Implementation"""
import zope.component
import zope.interface

from memphis.form import interfaces, widget
from memphis.form.widgets import text


class FileWidget(text.TextWidget):
    """Input type text widget implementation."""
    zope.interface.implementsOnly(interfaces.IWidget)

    klass = u'file-widget'

    # Filename and headers attribute get set by ``IDataConverter`` to the widget
    # provided by the FileUpload object of the form.
    headers = None
    filename = None
