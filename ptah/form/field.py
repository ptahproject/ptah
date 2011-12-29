import json
from collections import OrderedDict
from pyramid import renderers
from pyramid.compat import string_types

from ptah import config
from ptah.form.validator import All
from ptah.form.interfaces import _, null, required
from ptah.form.interfaces import Invalid, FORM_INPUT, FORM_DISPLAY

FIELD_ID = 'ptah.form:field'
PREVIEW_ID = 'ptah.form:field-preview'


class field(object):
    """ Field registration directive. Field should be inherited from
    :py:class:`ptah.form.Field` class.

    .. code-block:: python

      @form.field('text')
      class TextField(form.Field):
          ...

    """

    def __init__(self, name, __depth=1):
        self.info = config.DirectiveInfo(__depth)
        self.discr = (FIELD_ID, name)

        intr = config.Introspectable(FIELD_ID, self.discr, name, FIELD_ID)
        intr['name'] = name
        intr['codeinfo'] = self.info.codeinfo
        self.intr = intr

    @classmethod
    def register(cls, name, factory):
        cls(name, 2)(factory)

    def __call__(self, cls):
        cls.__field__ = self.intr['name']

        self.intr['field'] = cls
        self.info.attach(
            config.Action(
                lambda cfg, cls, name:
                    cfg.get_cfg_storage(FIELD_ID).update({name: cls}),
                (cls, self.intr['name']),
                discriminator=self.discr, introspectables=(self.intr,))
            )
        return cls


def fieldpreview(cls):
    """Register fieldpreview factory for field class.
    Fieldpreview factory is used in ``Field types`` management module.
    It should be an object that implements the
    :py:class:`ptah.form.interfaces.Preview` interface.

    .. code-block:: python

      @form.fieldpreview(form.TextField)
      def textPreview(request):
          field = form.TextField(
              'TextField',
              title = 'Text field',
              description = 'Text field preview description',
              default = 'Test text in text field.')

          widget = field.bind('preview.', form.null, {})
          widget.update(request)
          return widget.snippet('form-widget', widget)

    """
    info = config.DirectiveInfo()

    def wrapper(func):
        discr = (PREVIEW_ID, cls)
        intr = config.Introspectable(PREVIEW_ID, discr, '', PREVIEW_ID)
        intr['field'] = cls
        intr['preview'] = func

        info.attach(
            config.Action(
                lambda config, cls, func:
                    config.get_cfg_storage(PREVIEW_ID).update({cls: func}),
                (cls, func), discriminator=discr, introspectables=(intr,))
            )
        return func

    return wrapper


def get_field_factory(name):
    """Return field factory by name."""
    return config.get_cfg_storage(FIELD_ID).get(name, None)


def get_field_preview(cls):
    """Return field preview factory for field class."""
    return config.get_cfg_storage(PREVIEW_ID).get(cls, None)


class Fieldset(OrderedDict):
    """ """

    def __init__(self, *args, **kwargs):
        super(Fieldset, self).__init__()

        self.name = kwargs.pop('name', '')
        self.title = kwargs.pop('title', '')
        self.description = kwargs.pop('description', '')
        self.prefix = '%s.' % self.name if self.name else ''
        self.lprefix = len(self.prefix)

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

    def bind(self, data=None, params={}):
        clone = Fieldset(
            name=self.name,
            title=self.title,
            prefix=self.prefix,
            validator=self.validator.validators)

        if data is None:
            data = {}

        for name, field in self.items():
            if isinstance(field, Fieldset):
                clone[name] = field.bind(
                    data.get(name, None), params)
            else:
                clone[name] = field.bind(
                    self.prefix, data.get(name, null), params)

        clone.params = params
        clone.data = data
        return clone

    def extract(self):
        data = {}
        errors = FieldsetErrors(self)

        for fieldset in self.fieldsets():
            if fieldset is self:
                continue
            fdata, ferrors = fieldset.extract()
            data[fieldset.name] = fdata
            errors.extend(ferrors)

        for field in self.fields():
            if field.mode == FORM_DISPLAY:
                continue

            value = field.missing
            try:
                form = field.extract()

                value = field.deserialize(form)
                if value is null:
                    value = field.missing

                field.validate(value)

                if field.preparer is not None:
                    value = field.preparer(value)
            except Invalid as e:
                errors.append(e)

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
            r[err.field.name] = err.msg

        return r


class Field(object):
    """Field base class.

    ``name``: Name of this field.

    ``title``: The title of this field.  Defaults to a titleization
      of the ``name`` (underscores replaced with empty strings and the
      first letter of every resulting word capitalized).  The title is
      used by form for generating html form.

    ``description``: The description for this field.  Defaults to
      ``''`` (the empty string).  The description is used by form.

    ``validator``: Optional validator for this field.  It should be
      an object that implements the
      :py:class:`ptah.form.interfaces.Validator` interface.

    ``default``: Default field value.

    ``missing``: Field value if value is not specified in bound value.

    ``tmpl_input``: The path to input widget template. It should be
      compatible with pyramid renderers.

    ``tmpl_display``: The path to display widget template. It should be
      compatible with pyramid renderers.

    """

    __field__ = ''

    name = ''
    title = ''
    description = ''
    required = False
    error = None

    params = {}
    mode = None
    value = null
    form_value = None

    id = None
    klass = None

    tmpl_input = None
    tmpl_display = None

    def __init__(self, name, **kw):
        self.__dict__.update(kw)

        self.name = name
        self.title = kw.get('title', name.capitalize())
        self.description = kw.get('description', '')
        self.readonly = kw.get('readonly', None)
        self.default = kw.get('default', null)
        self.missing = kw.get('missing', required)
        self.preparer = kw.get('preparer', None)
        self.validator = kw.get('validator', None)
        self.required = self.missing is required

    def bind(self, prefix, value, params):
        """ Bind field to value and request params """
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.value = value
        clone.params = params
        clone.name = '%s%s' % (prefix, self.name)
        clone.id = clone.name.replace('.', '-')
        return clone

    def update(self, request):
        """ Update field, prepare field for rendering """
        self.request = request

        if self.mode is None:
            if self.readonly:
                self.mode = FORM_DISPLAY
            else:
                self.mode = FORM_INPUT

        # extract from request
        widget_value = self.extract()
        if widget_value is not null:
            self.form_value = widget_value
            return

        value = null

        # get from value
        if self.value is not null:
            value = self.value

        # use default
        if value is null:
            value = self.default

        # Convert the value to one that the widget can understand
        if value is not null:
            value = self.serialize(value)
            self.form_value = value if value is not null else None

    def serialize(self, value):
        """ Return value representation siutable for html widget """
        raise NotImplementedError()

    def deserialize(self, value):
        """ convert form value to field value """
        raise NotImplementedError()

    def dumps(self, value):
        """ return json value representation """
        return json.dumps(value)

    def loads(self, s):
        """ load field value from json """
        try:
            return json.loads(s)
        except Exception as e:
            raise Invalid(self, 'Error in JSON format: {0}'.format(s))

    def validate(self, value):
        """ validate value """
        if value is required:
            raise Invalid(self, _('Required'))

        if self.validator is not None:
            self.validator(self, value)

    def extract(self, default=null):
        """ extract value from params """
        value = self.params.get(self.name, default)
        if value is default or not value:
            return default
        return value

    def render(self, request):
        """ render field """
        if self.mode == FORM_DISPLAY:
            tmpl = self.tmpl_display
        else:
            tmpl = self.tmpl_input

        params = {'view': self,
                  'context': self,
                  'request': request}

        if isinstance(tmpl, string_types):
            return renderers.render(tmpl, params, request)
        else:
            return tmpl(**params)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class FieldFactory(Field):
    """ Create field by name. First argument name of field registered
    with :py:func:`ptah.form.field` decorator.

    Example:

    .. code-block:: python

       @form.field('customfield')
       class CustomField(form.Field):
           ...

       # Now `customfield` can be used for generating field:

       field = form.FieldFactory(
           'customfield', 'fieldname', ...)

    """

    __field__ = ''

    def __init__(self, typ, name, **kw):
        self.__field__ = typ

        super(FieldFactory, self).__init__(name, **kw)

    def bind(self, prefix, value, params):
        try:
            cls = config.get_cfg_storage(FIELD_ID)[self.__field__]
        except:
            cls = None

        if cls is None:
            raise TypeError(
                "Can't find field implementation for '%s'" % self.__field__)

        clone = cls.__new__(cls)
        clone.__dict__.update(self.__dict__)
        clone.value = value
        clone.params = params
        clone.name = '%s%s' % (prefix, self.name)
        return clone
