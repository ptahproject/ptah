##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""T Widget Implementation

$Id: file.py 11744 2011-01-28 09:15:15Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from memphis.form import interfaces, widget
from memphis.form.browser import text


class FileWidget(text.TextWidget):
    """Input type text widget implementation."""
    zope.interface.implementsOnly(interfaces.IFileWidget)

    klass = u'file-widget'

    # Filename and headers attribute get set by ``IDataConverter`` to the widget
    # provided by the FileUpload object of the form.
    headers = None
    filename = None


@zope.component.adapter(zope.schema.interfaces.IBytes, None)
@zope.interface.implementer(interfaces.IFieldWidget)
def FileFieldWidget(field, request):
    """IFieldWidget factory for FileWidget."""
    return widget.FieldWidget(field, FileWidget(request))
