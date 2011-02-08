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
"""Common z3c.form test setups"""

import os
import zope.component
import zope.interface
import zope.schema

from doctest import register_optionflag
from zope.schema.fieldproperty import FieldProperty

from pyramid.testing import DummyRequest as TestRequest

from memphis.form import browser, button, converter, datamanager, error, field
from memphis.form import form, interfaces, term, widget
from memphis.form.browser import radio, select, text, textarea

import lxml.html
import lxml.doctestcompare

# register lxml doctest option flags
lxml.doctestcompare.NOPARSE_MARKUP = register_optionflag('NOPARSE_MARKUP')


class TestingFileUploadDataConverter(converter.FileUploadDataConverter):
    """A special file upload data converter that works with testing."""
    zope.component.adapts(
        zope.schema.interfaces.IBytes, interfaces.IFileWidget)

    def toFieldValue(self, value):
        if value is None or value == '':
            value = self.widget.request.get(self.widget.name+'.testing', '')
            encoding = self.widget.request.get(
                self.widget.name+'.encoding', 'plain')

            # allow for the case where the file contents are base64 encoded.
            if encoding!='plain':
                value = value.decode(encoding)
            self.widget.request.form[self.widget.name] = value

        return super(TestingFileUploadDataConverter, self).toFieldValue(value)


def getPath(filename):
    return os.path.join(os.path.dirname(browser.__file__), filename)


##########################
def render(view, xpath='.'):
    method = getattr(view, 'render', None)
    if method is None:
        method = view.__call__

    string = method()
    if string == "":
        return string

    try:
        root = lxml.etree.fromstring(string)
    except lxml.etree.XMLSyntaxError:
        root = lxml.html.fromstring(string)

    output = ""
    for node in root.xpath(
        xpath, namespaces={'xmlns': 'http://www.w3.org/1999/xhtml'}):
        s = lxml.etree.tounicode(node, pretty_print=True)
        s = s.replace(' xmlns="http://www.w3.org/1999/xhtml"', ' ')
        output += s

    if not output:
        raise ValueError("No elements matched by %s." % repr(xpath))

    # let's get rid of blank lines
    output = output.replace('\n\n', '\n')

    # self-closing tags are more readable with a space before the
    # end-of-tag marker
    output = output.replace('"/>', '" />')

    return output
