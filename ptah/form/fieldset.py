""" Form Fieldset implementation """
import copy
from collections import OrderedDict
from pyramid.compat import text_type, string_types

from ptah.form.field import Field
from ptah.form.validator import All
from ptah.form.interfaces import null, Invalid


class Fieldset(OrderedDict):
    """ Fieldset holds fields """

    def __init__(self, *args, **kwargs):
        super(Fieldset, self).__init__()

        self.name = kwargs.pop('name', '')
        self.title = kwargs.pop('title', '')
        self.description = kwargs.pop('description', '')
        self.flat = kwargs.pop('flat', False)
        self.prefix = '%s.' % self.name if self.name else ''
        self.lprefix = len(self.prefix)
        self.filter = kwargs.pop('filter', None)

        validator = kwargs.pop('validator', None)
        if isinstance(validator, (tuple, list)):
            self.validator = All(*validator)
        else:
            self.validator = All()
            if validator is not None:
                self.validator.validators.append(validator)

        self.append(*args, **kwargs)

    def fields(self):
        for field in self.values():
            if isinstance(field, Field):
                yield field

    def fieldsets(self):
        yield self

        for fieldset in self.values():
            if isinstance(fieldset, Fieldset):
                yield fieldset

    def append(self, *args, **kwargs):
        for field in args:
            if isinstance(field, Field):
                if field.name in self:
                    raise ValueError("Duplicate name", field.name)
                self[field.name] = field

            elif isinstance(field, Fieldset):
                if field.name in self.name:
                    self.append(*field.values())
                    self.validator.validators.extend(field.validator.validators)
                    continue
                if field.name in self:
                    raise ValueError("Duplicate name", field.name)
                self[field.name] = field

            else:
                raise TypeError("Unrecognized argument type", field)

    def select(self, *names):
        return self.__class__(*[field for name, field in self.items()
                                if name in names])

    def omit(self, *names):
        return self.__class__(*[field for name, field in self.items()
                                if name not in names])

    def validate(self, data):
        self.validator(self, data)

    def bind(self, request, data=None, params={}, prefix='', context=None):
        clone = Fieldset(
            name=self.name,
            title=self.title,
            prefix=self.prefix,
            flat=self.flat,
            validator=self.validator.validators)

        if data is None or data is null:
            data = {}

        clone.request = request
        clone.params = params
        clone.data = data
        idprefix = '%s%s'%(self.prefix, prefix)

        for name, field in self.items():
            value = data if field.flat else data.get(name, null)

            if isinstance(field, Fieldset):
                clone[name] = field.bind(
                    request, value, params, idprefix, context)
            else:
                clone[name] = field.bind(
                    request, self.prefix, value, params, context)
                clone[name].set_id_prefix(idprefix)

        return clone

    def extract(self):
        data = {}
        errors = FieldsetErrors(self)

        for fieldset in self.fieldsets():
            if fieldset is self:
                continue

            fdata, ferrors = fieldset.extract()
            if fieldset.flat:
                data.update(fdata)
            else:
                data[fieldset.name] = fdata
            errors.extend(ferrors)

        for field in self.fields():
            value = field.extract()

            if value is not null:
                try:
                    value = field.to_field(value)
                except Invalid as e:
                    data[field.name[self.lprefix:]] = value
                    errors.append(e)
                    continue

            if value is null and field.missing is not null:
                value = copy.copy(field.missing)

            try:
                field.validate(value)
            except Invalid as e:
                errors.append(e)

            if field.preparer is not None:
                value = field.preparer(value)

            if field.flat:
                data.update(field.flatten(value))
            else:
                data[field.name[self.lprefix:]] = value

        if not errors:
            try:
                self.validate(data)
            except Invalid as e:
                errors.append(e)

        return data, errors

    def __add__(self, fieldset):
        if not isinstance(fieldset, Fieldset):
            raise ValueError(fieldset)

        return self.__class__(self, fieldset)


class FieldsetErrors(list):

    def __init__(self, fieldset, *args):
        super(FieldsetErrors, self).__init__(args)

        self.fieldset = fieldset

    @property
    def msg(self):
        r = {}
        for err in self:
            r[err.field.name] = text_type(err)

        return r

    def append(self, err):
        """
        Append error to fieldset errors. If err is tuple of two values,
        then first element acts as name and second as err for `add_field_error`
        call.
        """
        if isinstance(err, tuple):
            self.add_field_error(*err)
        else:
            super(FieldsetErrors, self).append(err)

    def add_field_error(self, name, err):
        """
        Add error to specific field. Set error `field` to specified field.
        """
        if isinstance(err, string_types):
            err = Invalid(err)

        field = self.fieldset[name]

        err.field = field
        if field.error is None:
            field.error = err

        self.append(err)

    def __contains__(self, name):
        """
        Check if there is error for field
        """
        if isinstance(name, Invalid):
            return super(FieldsetErrors, self).__contains__(name)

        for err in self:
            if (err.field and err.field.name == name) or (err.name == name):
                return True
