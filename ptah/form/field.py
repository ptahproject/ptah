from ptah import config, view
from collections import OrderedDict

from validator import All
from interfaces import _, null, required
from interfaces import Invalid, FORM_INPUT, FORM_DISPLAY

FIELD_ID = 'ptah.form:field'
PREVIEW_ID = 'ptah.form:field-preview'


def field(name, layer=''):
    info = config.DirectiveInfo(allowed_scope=('class',))

    discriminator = (FIELD_ID, name, layer)

    info.attach(
        config.ClassAction(
            view.LayerWrapper(register_field_impl, discriminator),
            (name, ),
            discriminator=discriminator)
        )


def register_field_factory(cls, name, layer=''):
    info = config.DirectiveInfo()

    discriminator = (FIELD_ID, name, layer)

    info.attach(
        config.Action(
            view.LayerWrapper(register_field_impl, discriminator),
            (cls, name),
            discriminator=discriminator)
        )


def fieldpreview(cls):
    info = config.DirectiveInfo()

    def wrapper(func):
        info.attach(
            config.Action(
                lambda config, cls, func:
                    config.get_cfg_storage(PREVIEW_ID).update({cls: func}),
                (cls, func),
                discriminator=(PREVIEW_ID, cls))
            )
        return func

    return wrapper


def register_field_impl(cfg, cls, name):
    cls.__field__ = name
    cfg.get_cfg_storage(FIELD_ID)[name] = cls


def get_field_factory(name):
    return config.get_cfg_storage(FIELD_ID).get(name, None)


def get_field_preview(cls):
    return config.get_cfg_storage(PREVIEW_ID).get(cls, None)


class Fieldset(OrderedDict):

    def __init__(self, *args, **kwargs):
        super(Fieldset, self).__init__()

        self.name = kwargs.pop('name', u'')
        self.legend = kwargs.pop('legend', u'')
        self.prefix = '%s.' % self.name if self.name else ''
        self.lprefix = len(self.prefix)

        validator = kwargs.pop('validator', None)
        if type(validator) is list:
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
            legend=self.legend,
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
            except Invalid, error:
                errors.append(error)

            data[field.name[self.lprefix:]] = value

        if not errors:
            try:
                self.validate(data)
            except Invalid, error:
                errors.append(error)

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
    """Widget base class."""

    __field__ = ''

    name = ''
    title = u''
    description = u''
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
        self.description = kw.get('description', u'')
        self.readonly = kw.get('readonly', None)
        self.default = kw.get('default', null)
        self.missing = kw.get('missing', required)
        self.preparer = kw.get('preparer', None)
        self.validator = kw.get('validator', None)
        self.required = self.missing is required

    def bind(self, prefix, value, params):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.value = value
        clone.params = params
        clone.name = '%s%s' % (prefix, self.name)
        clone.id = clone.name.replace('.', '-')
        return clone

    def update(self, request):
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
        raise NotImplementedError()

    def deserialize(self, value):
        raise NotImplementedError()

    def validate(self, value):
        if value is required:
            raise Invalid(self, _('Required'))

        if self.validator is not None:
            self.validator(self, value)

    def extract(self, default=null):
        value = self.params.get(self.name, default)
        if value is default or not value:
            return default
        return value

    def render(self, request):
        if self.mode == FORM_DISPLAY:
            return self.tmpl_display(
                view=view,
                context=self,
                request=request)
        else:
            return self.tmpl_input(
                view=self,
                context=self,
                request=request)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class FieldFactory(Field):

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
