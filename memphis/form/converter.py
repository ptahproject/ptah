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
"""Data Converters"""
import datetime
import decimal
import zope.i18n.format
import zope.interface
import zope.component
import zope.schema
from pyramid.i18n import get_locale_name
from zope.i18n.locales import locales

from memphis import config
from memphis.form import interfaces

_ = interfaces.MessageFactory


def getLocale(request):
    return locales.getLocale(get_locale_name(request), None, None)


class BaseDataConverter(object):
    """A base implementation of the data converter."""
    zope.interface.implements(interfaces.IDataConverter)

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return u''
        return unicode(value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        return self.field.fromUnicode(value)

    def __repr__(self):
        return '<%s converts from %s to %s>' %(
            self.__class__.__name__,
            self.field.__class__.__name__,
            self.widget.__class__.__name__)


class FieldDataConverter(BaseDataConverter):
    """A data converter using the field's ``fromUnicode()`` method."""
    config.adapts(zope.schema.interfaces.IField, interfaces.IWidget)

    def __init__(self, field, widget):
        super(FieldDataConverter, self).__init__(field, widget)
        if not zope.schema.interfaces.IFromUnicode.providedBy(field):
            fieldName = ''
            if field.__name__:
                fieldName = '``%s`` ' % field.__name__
            raise TypeError(
                'Field %sof type ``%s`` must provide ``IFromUnicode``.' %(
                    fieldName, type(field).__name__))


@config.adapter(interfaces.IWidget)
@zope.interface.implementer(interfaces.IDataConverter)
def FieldWidgetDataConverter(widget):
    """Provide a data converter based on a field widget."""
    return zope.component.queryMultiAdapter(
        (widget.field, widget), interfaces.IDataConverter)


class FormatterValidationError(zope.schema.ValidationError):

    message = None # redefine here, so Python 2.6 won't raise warning

    def __init__(self, message, value):
        zope.schema.ValidationError.__init__(self, message, value)
        self.message = message

    def doc(self):
        return self.message


class NumberDataConverter(BaseDataConverter):
    """A general data converter for numbers."""

    type = None
    errorMessage = None

    def __init__(self, field, widget):
        super(NumberDataConverter, self).__init__(field, widget)
        locale = getLocale(self.widget.request)
        self.formatter = locale.numbers.getFormatter('decimal')
        self.formatter.type = self.type

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return u''
        return self.formatter.format(value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        try:
            return self.formatter.parse(value)
        except zope.i18n.format.NumberParseError:
            raise FormatterValidationError(self.errorMessage, value)


class IntegerDataConverter(NumberDataConverter):
    """A data converter for integers."""
    config.adapts(
        zope.schema.interfaces.IInt, interfaces.IWidget)
    type = int
    errorMessage = _('The entered value is not a valid integer literal.')


class FloatDataConverter(NumberDataConverter):
    """A data converter for integers."""
    config.adapts(zope.schema.interfaces.IFloat, interfaces.IWidget)
    type = float
    errorMessage = _('The entered value is not a valid decimal literal.')


class DecimalDataConverter(NumberDataConverter):
    """A data converter for integers."""
    config.adapts(zope.schema.interfaces.IDecimal, interfaces.IWidget)
    type = decimal.Decimal
    errorMessage = _('The entered value is not a valid decimal literal.')


class CalendarDataConverter(BaseDataConverter):
    """A special data converter for calendar-related values."""

    type = None
    length = 'short'

    def __init__(self, field, widget):
        super(CalendarDataConverter, self).__init__(field, widget)
        locale = getLocale(self.widget.request)
        self.formatter = locale.dates.getFormatter(self.type, self.length)

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return u''
        return self.formatter.format(value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        try:
            return self.formatter.parse(value)
        except zope.i18n.format.DateTimeParseError, err:
            raise FormatterValidationError(err.args[0], value)


class DateDataConverter(CalendarDataConverter):
    """A special data converter for dates."""
    config.adapts(zope.schema.interfaces.IDate, interfaces.IWidget)
    type = 'date'


class TimeDataConverter(CalendarDataConverter):
    """A special data converter for times."""
    config.adapts(zope.schema.interfaces.ITime, interfaces.IWidget)
    type = 'time'


class DatetimeDataConverter(CalendarDataConverter):
    """A special data converter for datetimes."""
    config.adapts(zope.schema.interfaces.IDatetime, interfaces.IWidget)
    type = 'dateTime'


class TimedeltaDataConverter(FieldDataConverter):
    """A special data converter for timedeltas."""
    config.adapts(zope.schema.interfaces.ITimedelta, interfaces.IWidget)

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        daysString, crap, timeString = value.split(' ')
        days = int(daysString)
        seconds = [int(part)*60**(2-n)
                   for n, part in enumerate(timeString.split(':'))]
        return datetime.timedelta(days, sum(seconds))


class FileUploadDataConverter(BaseDataConverter):
    """A special data converter for bytes, supporting also FileUpload.

    Since IBytes represents a file upload too, this converter can handle
    zope.publisher.browser.FileUpload object as given value.
    """
    config.adapts(zope.schema.interfaces.IBytes, interfaces.IFileWidget)

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        return value

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value is None or value == '':
            # When no new file is uploaded, send a signal that we do not want
            # to do anything special.
            return interfaces.NOT_CHANGED

        if isinstance(value, zope.publisher.browser.FileUpload):
            # By default a IBytes field is used for get a file upload widget.
            # But interfaces extending IBytes do not use file upload widgets.
            # Any way if we get a FileUpload object, we'll convert it.
            # We also store the additional FileUpload values on the widget
            # before we loose them.
            self.widget.headers = value.headers
            self.widget.filename = value.filename
            try:
                seek = value.seek
                read = value.read
            except AttributeError, e:
                raise ValueError(_('Bytes data are not a file object'), e)
            else:
                seek(0)
                data = read()
                if data or getattr(value, 'filename', ''):
                    return data
                else:
                    return self.field.missing_value
        else:
            return str(value)


class SequenceDataConverter(BaseDataConverter):
    """Basic data converter for ISequenceWidget."""
    config.adapts(zope.schema.interfaces.IField, interfaces.ISequenceWidget)

    def toWidgetValue(self, value):
        """Convert from Python bool to HTML representation."""
        widget = self.widget
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return []
        # Look up the term in the terms
        terms = widget.updateTerms()
        try:
            return [terms.getTerm(value).token]
        except LookupError:
            # Swallow lookup errors, in case the options changed.
            return []

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if not len(value) or value[0] == widget.noValueToken:
            return self.field.missing_value
        widget.updateTerms()
        return widget.terms.getValue(value[0])


class CollectionSequenceDataConverter(BaseDataConverter):
    """A special converter between collections and sequence widgets."""
    config.adapts(zope.schema.interfaces.ICollection, 
                  interfaces.ISequenceWidget)

    def toWidgetValue(self, value):
        """Convert from Python bool to HTML representation."""
        if value is self.field.missing_value:
            return []
        widget = self.widget
        if widget.terms is None:
            widget.updateTerms()
        values = []
        for entry in value:
            try:
                values.append(widget.terms.getTerm(entry).token)
            except LookupError, err:
                # Swallow lookup errors, in case the options changed.
                pass
        return values

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if widget.terms is None:
            widget.updateTerms()
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        return collectionType([widget.terms.getValue(token) for token in value])


class TextLinesConverter(BaseDataConverter):
    """Data converter for ITextLinesWidget."""
    config.adapts(zope.schema.interfaces.ISequence, interfaces.ITextLinesWidget)

    def toWidgetValue(self, value):
        """Convert from text lines to HTML representation."""
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return u''
        return u'\n'.join(unicode(v) for v in value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        if not len(value):
            return self.field.missing_value
        valueType = self.field.value_type._type
        if isinstance(valueType, tuple):
            valueType = valueType[0]
        return collectionType(valueType(v) for v in value.splitlines())


class BoolSingleCheckboxDataConverter(BaseDataConverter):
    "A special converter between boolean fields and single checkbox widgets."
    config.adapts(zope.schema.interfaces.IBool, 
                  interfaces.ISingleCheckBoxWidget)

    def toWidgetValue(self, value):
        """Convert from Python bool to HTML representation."""
        if value:
            return ['selected']
        return []

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value and value[0] == 'selected':
            return True
        return False
