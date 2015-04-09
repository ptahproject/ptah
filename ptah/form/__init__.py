# ptah.form public api

__all__ = [
    'null', 'Invalid', 'FieldsetErrors',
    'Field', 'FieldFactory', 'Fieldset',
    'field', 'fieldpreview', 'get_field_factory', 'get_field_preview',

    'Term', 'Vocabulary',

    'All','Function','Regex','Email','Range', 'Length','OneOf',

    'CompositeField', 'CompositeError',

    'InputField', 'OptionsField',
    'VocabularyField', 'BaseChoiceField','BaseMultiChoiceField',

    'TextField','IntegerField','FloatField',
    'DecimalField','TextAreaField','FileField','LinesField','PasswordField',
    'DateField','DateTimeField','RadioField','BoolField','ChoiceField',
    'MultiChoiceField','MultiSelectField','TimezoneField',

    'Form','FormWidgets',
    'button','button2','Button','Buttons',

    'AC_DEFAULT','AC_PRIMARY','AC_DANGER','AC_SUCCESS','AC_INFO','AC_WARNING',

    'parse_date','includeme', 'reify',
]

try:
    from collections import OrderedDict
    OrderedDict
except ImportError: # pragma: no cover
    import collections
    from ordereddict import OrderedDict
    collections.OrderedDict = OrderedDict
    OrderedDict

from pyramid.decorator import reify

# validation
from ptah.form.interfaces import null
from ptah.form.interfaces import Invalid

# field
from ptah.form.field import Field
from ptah.form.field import FieldFactory

from ptah.form.fieldset import Fieldset
from ptah.form.fieldset import FieldsetErrors

# field registration
from ptah.form.directives import field
from ptah.form.directives import fieldpreview
from ptah.form.directives import get_field_factory
from ptah.form.directives import get_field_preview

# vocabulary
from ptah.form.vocabulary import Term
from ptah.form.vocabulary import Vocabulary

# validators
from ptah.form.validator import All
from ptah.form.validator import Function
from ptah.form.validator import Regex
from ptah.form.validator import Email
from ptah.form.validator import Range
from ptah.form.validator import Length
from ptah.form.validator import OneOf

# helper class
from ptah.form.field import InputField

# helper field classes
from ptah.form.fields import VocabularyField
from ptah.form.fields import BaseChoiceField
from ptah.form.fields import BaseMultiChoiceField

# fields
from ptah.form.fields import TextField
from ptah.form.fields import IntegerField
from ptah.form.fields import FloatField
from ptah.form.fields import DecimalField
from ptah.form.fields import TextAreaField
from ptah.form.fields import FileField
from ptah.form.fields import LinesField
from ptah.form.fields import PasswordField
from ptah.form.fields import DateField
from ptah.form.fields import DateTimeField
from ptah.form.fields import RadioField
from ptah.form.fields import BoolField
from ptah.form.fields import ChoiceField
from ptah.form.fields import MultiChoiceField
from ptah.form.fields import MultiSelectField
from ptah.form.fields import TimezoneField
from ptah.form.fields import OptionsField

# composite fields
from ptah.form.composite import CompositeField
from ptah.form.composite import CompositeError

# forms
from ptah.form.form import Form
from ptah.form.form import FormWidgets

# button
from ptah.form.button import button
from ptah.form.button import button2
from ptah.form.button import Button
from ptah.form.button import Buttons
from ptah.form.button import AC_DEFAULT
from ptah.form.button import AC_PRIMARY
from ptah.form.button import AC_DANGER
from ptah.form.button import AC_SUCCESS
from ptah.form.button import AC_INFO
from ptah.form.button import AC_WARNING

# iso date
from ptah.form.iso8601 import parse_date


def includeme(cfg):
    cfg.include('pyramid_chameleon')
    cfg.include('ptah.renderer')

    # field
    from ptah.form.directives import add_field
    cfg.add_directive('provide_form_field', add_field)

    # layers
    cfg.add_layer('form', path='ptah.form:templates/')

    # scan
    cfg.scan('ptah.form')
