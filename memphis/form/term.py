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
"""Terms Implementation

$Id: term.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
import colander
import zope.component
import zope.schema
from zope.schema import vocabulary

from memphis import config
from memphis.form import interfaces

_ = interfaces.MessageFactory


class Terms(object):
    """Base implementation for custom ITerms."""

    zope.interface.implements(interfaces.ITerms)

    def getTerm(self, value):
        return self.terms.getTerm(value)

    def getTermByToken(self, token):
        return self.terms.getTermByToken(token)

    def getValue(self, token):
        return self.terms.getTermByToken(token).value

    def __iter__(self):
        return iter(self.terms)

    def __len__(self):
        return self.terms.__len__()

    def __contains__(self, value):
        return self.terms.__contains__(value)


@config.adapter(
    zope.interface.Interface,
    colander.SchemaNode,
    colander.SchemaType,
    interfaces.IWidget)
@zope.interface.implementer(interfaces.ITerms)
def ChoiceTerms(context, field, typ, widget):
    terms = getattr(field, 'vocabulary', None)
    return zope.component.queryMultiAdapter(
        (context, field, terms, widget), interfaces.ITerms)


class ChoiceTermsVocabulary(Terms):
    """ITerms adapter for zope.schema.IChoice based implementations using
    vocabulary."""
    config.adapts(
        zope.interface.Interface,
        colander.SchemaNode,
        zope.schema.interfaces.IBaseVocabulary,
        interfaces.IWidget)

    zope.interface.implements(interfaces.ITerms)

    def __init__(self, context, field, vocabulary, widget):
        self.context = context
        self.field = field
        self.widget = widget
        self.terms = vocabulary


class BoolTerms(Terms):
    """Default yes and no terms are used by default for IBool fields."""
    config.adapts(
        zope.interface.Interface,
        colander.SchemaNode,
        colander.Bool,
        interfaces.IWidget)

    zope.interface.implementsOnly(interfaces.IBoolTerms)

    trueLabel = _('yes')
    falseLabel = _('no')

    def __init__(self, context, field, typ, widget):
        self.context = context
        self.field = field
        self.typ = typ
        self.widget = widget
        terms = [vocabulary.SimpleTerm(*args)
                 for args in [(True, 'true', self.trueLabel),
                              (False, 'false', self.falseLabel)]]
        self.terms = vocabulary.SimpleVocabulary(terms)


@config.adapter(
    zope.interface.Interface,
    zope.interface.Interface,
    zope.interface.Interface,
    zope.schema.interfaces.ICollection,
    interfaces.IWidget)
@zope.interface.implementer(interfaces.ITerms)
def CollectionTerms(context, request, form, field, widget):
    terms = field.value_type.bind(context or widget.context).vocabulary
    return zope.component.queryMultiAdapter(
        (context, request, form, field, terms, widget),
        interfaces.ITerms)


class CollectionTermsVocabulary(Terms):
    """ITerms adapter for zope.schema.ICollection based implementations using
    vocabulary."""
    config.adapts(
        zope.interface.Interface,
        zope.interface.Interface,
        zope.interface.Interface,
        zope.schema.interfaces.ICollection,
        zope.schema.interfaces.IBaseVocabulary,
        interfaces.IWidget)

    def __init__(self, context, request, form, field, vocabulary, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.terms = vocabulary
