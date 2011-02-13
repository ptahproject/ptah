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
"""Widget Framework Implementation

$Id: widget.py 11799 2011-01-31 04:27:03Z fafhrd91 $
"""
__docformat__ = "reStructuredText"

from zope.component import getMultiAdapter
import zope.interface
import zope.component
import zope.schema.interfaces
#from zope.i18n import translate
from zope.schema.fieldproperty import FieldProperty

from memphis import view
from memphis.form import interfaces, util

from pagelets import \
    IWidgetInputView, IWidgetDisplayView, IWidgetHiddenView


PLACEHOLDER = object()


class Widget(object):
    """Widget base class."""

    zope.interface.implements(interfaces.IWidget)

    # widget specific attributes
    name = FieldProperty(interfaces.IWidget['name'])
    label = FieldProperty(interfaces.IWidget['label'])
    mode = FieldProperty(interfaces.IWidget['mode'])
    required = FieldProperty(interfaces.IWidget['required'])
    error = FieldProperty(interfaces.IWidget['error'])
    value = FieldProperty(interfaces.IWidget['value'])
    ignoreRequest = FieldProperty(interfaces.IWidget['ignoreRequest'])
    setErrors = FieldProperty(interfaces.IWidget['setErrors'])

    # The following attributes are for convenience. They are declared in
    # extensions to the simple widget.

    # See ``interfaces.IContextAware``
    context = None
    ignoreContext = False
    # See ``interfaces.IFormAware``
    form = None

    def __init__(self, field, request):
        self.field = field
        self.request = request

        self.name = field.__name__
        self.id = field.__name__.replace('.', '-')
        self.label = field.title
        self.required = field.required

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Step 1: Determine the value.
        value = interfaces.NO_VALUE
        lookForDefault = False
        # Step 1.1: If possible, get a value from the request
        if not self.ignoreRequest:
            #at this turn we do not need errors to be set on widgets
            #errors will be set when extract gets called from form.extractData
            self.setErrors = False
            widget_value = self.extract()
            if widget_value is not interfaces.NO_VALUE:
                # Once we found the value in the request, it takes precendence
                # over everything and nothing else has to be done.
                self.value = widget_value
                value = PLACEHOLDER

        # Step 1.2: If we have a widget with a field and we have no value yet,
        #           we have some more possible locations to get the value
        if value is interfaces.NO_VALUE and value is not PLACEHOLDER:
            # Step 1.2.1: If the widget knows about its context and the
            #              context is to be used to extract a value, get
            #              it now via a data manager.
            if (interfaces.IContextAware.providedBy(self) and
                not self.ignoreContext):
                value = zope.component.getMultiAdapter(
                    (self.context, self.field),
                    interfaces.IDataManager).query()
            # Step 1.2.2: If we still do not have a value, we can always use
            #             the default value of the field, id set
            # NOTE: It should check field.default is not missing_value, but
            # that requires fixing zope.schema first
            if ((value is self.field.missing_value or
                 value is interfaces.NO_VALUE) and
                self.field.default is not None):
                value = self.field.default
                lookForDefault = True

        # Step 1.3: If we still have not found a value, then we try to get it
        #           from an attribute value
        # remove during simplification

        # Step 1.4: Convert the value to one that the widget can understand
        if value not in (interfaces.NO_VALUE, PLACEHOLDER):
            converter = interfaces.IDataConverter(self)
            self.value = converter.toWidgetValue(value)

    def render(self):
        """See memphis.form.interfaces.IWidget."""
        m = {
            interfaces.INPUT_MODE: IWidgetInputView,
            interfaces.DISPLAY_MODE: IWidgetDisplayView,
            interfaces.HIDDEN_MODE: IWidgetHiddenView}

        return view.renderPagelet(m[self.mode], self, self.request)

    def extract(self, default=interfaces.NO_VALUE):
        """See memphis.form.interfaces.IWidget."""
        return self.request.params.get(self.name, default)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class SequenceWidget(Widget):
    """Term based sequence widget base.

    The sequence widget is used for select items from a sequence. Don't get
    confused, this widget does support to choose one or more values from a
    sequence. The word sequence is not used for the schema field, it's used
    for the values where this widget can choose from.

    This widget base class is used for build single or sequence values based
    on a sequence which is in most use case a collection. e.g.
    IList of IChoice for sequence values or IChoice for single values.

    See also the MultiWidget for build sequence values based on none collection
    based values. e.g. IList of ITextLine
    """

    zope.interface.implements(interfaces.ISequenceWidget)

    value = ()
    terms = None

    noValueToken = '--NOVALUE--'

    @property
    def displayValue(self):
        value = []
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.noValueToken:
                continue
            term = self.terms.getTermByToken(token)
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                #value.append(translate(
                #    term.title, context=self.request, default=term.title))
                value.append(term.title)
            else:
                value.append(term.value)
        return value

    def updateTerms(self):
        if self.terms is None:
            self.terms = zope.component.getMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.ITerms)
        return self.terms

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Create terms first, since we need them for the generic update.
        self.updateTerms()
        super(SequenceWidget, self).update()

    def extract(self, default=interfaces.NO_VALUE):
        """See z3c.form.interfaces.IWidget."""
        if (self.name not in self.request.params and
            self.name+'-empty-marker' in self.request.params):
            return interfaces.NO_VALUE
        value = self.request.params.get(self.name, default)
        if value != default:
            if not isinstance(value, (tuple, list)):
                value = (value,)
            # do some kind of validation, at least only use existing values
            for token in value:
                if token == self.noValueToken:
                    continue
                try:
                    self.terms.getTermByToken(token)
                except LookupError:
                    return default
        return value
