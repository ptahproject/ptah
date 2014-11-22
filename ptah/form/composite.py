""" Composite Field """
import copy
import pprint
from pyramid.decorator import reify

from ptah.form.field import Field
from ptah.form.fieldset import Fieldset
from ptah.form.interfaces import null, Invalid


class CompositeError(Invalid):

    def __repr__(self):
        n = self.field.name if self.field else ''
        return 'CompositeError<%s%s>:\n%s' % (
            n, ': %s'%self.msg if self.msg else '',
            pprint.pformat(self.errors, 4))


class CompositeField(Field):
    """ Composit field """

    fields = None
    tmpl_input = 'form:composite'
    tmpl_widget = 'form:widget-composite'

    inline = False
    consolidate_errors = False

    def __init__(self, *args, **kw):
        super(CompositeField, self).__init__(*args, **kw)

        if not self.fields:
            raise ValueError('Fields are required for composite field.')

        if not isinstance(self.fields, Fieldset):
            self.fields = Fieldset(*self.fields)

        self.fields.prefix = '%s.'%self.name

    @reify
    def default(self):
        return dict(
            [(name,
              field.default if field.default is not null else field.missing)
             for name, field in self.fields.items()])

    def bind(self, request, prefix, value, params, context=None):
        """ Bind field to value and request params """
        if value in (null, None):
            value = {}

        clone = super(CompositeField, self).bind(
            request, prefix, value, params, context)

        clone.fields = self.fields.bind(request, value, params, '', context)
        return clone

    def set_id_prefix(self, prefix):
        self.id = ('%s%s'%(prefix, self.name)).replace('.', '-')

        prefix = '%s%s.'%(prefix, self.name)

        for name, field in self.fields.items():
            field.set_id_prefix(prefix)

    def update(self):
        """ Update field, prepare field for rendering """
        super(CompositeField, self).update()

        for field in self.fields.values():
            field.update()

    def to_field(self, value):
        """ convert form value to field value """
        result = {}
        errors = []
        for name, val in value.items():
            field = self.fields[name]
            try:
                result[name] = field.to_field(val)
            except Invalid as error:
                error.name = name
                errors.append(error)
                if field.error is None:
                    field.error = error

        if errors:
            if self.consolidate_errors:
                raise CompositeError(errors[0].msg, field=self)
            else:
                raise CompositeError(field=self, errors=errors)

        return result

    def validate(self, value):
        """ validate value """
        errors = []
        for name, val in value.items():
            field = self.fields[name]
            try:
                field.validate(val)
            except Invalid as error:
                error.name = name
                errors.append(error)
                if field.error is None:
                    field.error = error

        if errors:
            if self.consolidate_errors:
                raise CompositeError(errors[0].msg, field=self)
            else:
                raise CompositeError(field=self, errors=errors)

        if self.validator is not None:
            self.validator(self, value)

    def extract(self):
        value = {}
        for name, field in self.fields.items():
            val = field.extract()
            if val is null and field.missing is not null:
                val = copy.copy(field.missing)

            value[name] = val

        return value

    def flatten(self, value):
        for name, field in self.fields.items():
            if field.flat and name in value:
                value.update(field.flatten(value.pop(name)))

        return value
