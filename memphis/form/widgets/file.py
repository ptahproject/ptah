"""File Widget Implementation"""
import zope.component
import zope.interface
import zope.schema.interfaces

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


@zope.component.adapter(zope.schema.interfaces.IBytes, None)
@zope.interface.implementer(interfaces.IWidget)
def FileFieldWidget(field, request):
    """IWidget factory for FileWidget."""
    return widget.FieldWidget(field, FileWidget(request))
