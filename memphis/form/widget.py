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
""" Widget Framework Implementation """
from zope import interface
from zope.component import getMultiAdapter
from zope.schema.interfaces import IField, ITitledTokenizedTerm

from webob.multidict import MultiDict

from memphis import view, config
from memphis.form import interfaces, util


PLACEHOLDER = object()

@config.adapter(IField, None)
@interface.implementer(interfaces.IDefaultWidget)
def getDefaultWidget(field, request):
    return getMultiAdapter((field, request), interfaces.IWidget)


class Widget(object):
    """Widget base class."""
    interface.implements(interfaces.IWidget)

    # widget specific attributes
    name = '' 
    label = u''
    mode = interfaces.INPUT_MODE
    required = False 
    error = None 
    value = None 
    setErrors = True

    form = None
    content = None

    def __init__(self, field, request):
        self.field = field
        self.request = request
        self.params = MultiDict({})

        self.name = field.__name__
        self.id = field.__name__.replace('.', '-')
        self.label = field.title
        self.required = field.required

    @property
    def __title__(self):
        return self.__class__.__name__

    def update(self):
        # Step 1: Determine the value.
        value = interfaces.NO_VALUE
        lookForDefault = False

        # Step 1.1: If possible, get a value from the request
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
            # Step 1.2.1: If the widget knows about its content and the
            #              content is to be used to extract a value, get
            #              it now via a data manager.
            if self.content is not None:
                value = getMultiAdapter(
                    (self.content, self.field), interfaces.IDataManager).query()
            # Step 1.2.2: If we still do not have a value, we can always use
            #             the default value of the field, id set
            # NOTE: It should check field.default is not missing_value, but
            # that requires fixing zope.schema first
            if ((value is self.field.missing_value or
                 value is interfaces.NO_VALUE) and
                self.field.default is not None):
                value = self.field.default
                lookForDefault = True

        # Step 1.4: Convert the value to one that the widget can understand
        if value not in (interfaces.NO_VALUE, PLACEHOLDER):
            self.value = getMultiAdapter(
                (self.field, self), 
                interfaces.IDataConverter).toWidgetValue(value)

    def render(self):
        # render pagelet, check memphis/form/pagelets.py
        return getMultiAdapter((self, self.request), self.mode)()

    def extract(self, default=interfaces.NO_VALUE):
        return self.params.get(self.name, default)

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
    interface.implements(interfaces.ISequenceWidget)

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
            if ITitledTokenizedTerm.providedBy(term):
                value.append(
                    view.translate(
                        term.title, context=self.request, default=term.title))
            else:
                value.append(term.value)
        return value

    def updateTerms(self):
        if self.terms is None:
            self.terms = getMultiAdapter(
                (self.content, self.request, self.form, self.field, self),
                interfaces.ITerms)
        return self.terms

    def update(self):
        # Create terms first, since we need them for the generic update.
        self.updateTerms()
        super(SequenceWidget, self).update()

    def extract(self, default=interfaces.NO_VALUE):
        if (self.name not in self.params and
            self.name+'-empty-marker' in self.params):
            return default
        value = self.params.getall(self.name) or default
        if value != default:
            # do some kind of validation, at least only use existing values
            for token in value:
                if token == self.noValueToken:
                    continue
                try:
                    self.terms.getTermByToken(token)
                except LookupError:
                    return default
        return value
