from memphis import config, view
from collections import OrderedDict

from validator import All
from interfaces import _, null, required, Invalid, FORM_INPUT, FORM_DISPLAY


fields = {}

def field(name, layer=''):
    info = config.DirectiveInfo(allowed_scope=('class',))

    discriminator = ('memphis.form:field', name, layer)

    info.attach(
        config.ClassAction(
            view.LayerWrapper(registerFieldImpl, discriminator),
            (name, ), discriminator = discriminator)
        )


def registerField(cls, name, layer=''):
    info = config.DirectiveInfo()

    discriminator = ('memphis.form:field', name, layer)

    info.attach(
        config.Action(
            view.LayerWrapper(registerFieldImpl, discriminator),
            (cls, name),
            discriminator = discriminator)
        )

def registerFieldImpl(cls, name):
    fields[name] = cls
    cls.__field__ = name


def getField(name):
    return fields.get(name, None)


class Fieldset(OrderedDict):

    def __init__(self, *args, **kwargs):
        super(Fieldset, self).__init__()

        self.name = kwargs.pop('name', u'')
        self.legend = kwargs.pop('legend', u'')
        self.prefix = '%s.'%self.name if self.name else ''
        self.lprefix = len(self.prefix)

        self.validator = All()
        validator = kwargs.pop('validator', None)
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

    def bind(self, content=None, params={}):
        clone = Fieldset(
            name = self.name,
            legend = self.legend,
            prefix = self.prefix,
            validator = self.validator)

        if content is None:
            content = {}

        for name, field in self.items():
            clone[name] = field.bind(
                self.prefix, content.get(name, null), params)

        clone.params = params
        clone.content = content
        return clone

    def extract(self):
        data = {}
        errors = []

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

            data[field.name] = value

        if not errors:
            try:
                self.validate(data)
            except Invalid, error:
                errors.append(error)

        return data, FieldsetErrors(self, errors)

    def __add__(self, fieldset):
        if not isinstance(fieldset, Fieldset):
            raise ValueError(fieldset)

        return self.__class__(self, fieldset)


class FieldsetErrors(list):

    def __init__(self, fieldset, *args):
        super(FieldsetErrors, self).__init__(*args)

        self.fieldset = fieldset

    @property
    def message(self):
        return self.as_dict()

    def as_dict(self):
        r = {}
        for err in self:
            r[err.field.name] = err.message

        return r


class Field(object):
    """Widget base class."""

    __field__ = ''

    name = ''
    title = u''
    description = u''
    required = False

    error = None
    content = None
    params = {}
    localizer = None
    value = null
    mode = FORM_INPUT

    id = None
    klass = None

    tmpl_input = None
    tmpl_display = None

    def __init__(self, name, **kw):
        self.name = name
        self.title = kw.get('title', name.capitalize())
        self.description = kw.get('description', u'')
        self.readonly = kw.get('readonly', None)
        self.default = kw.get('missing', null)
        self.missing = kw.get('missing', required)
        self.preparer = kw.get('preparer', None)
        self.validator = kw.get('validator', None)
        self.required = self.missing is required

    def bind(self, prefix, content, params):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.content = content
        clone.params = params
        clone.name = '%s%s'%(prefix, self.name)
        return clone

    def update(self, request):
        self.request = request

        value = null

        # Step 1.1: extract from request
        widget_value = self.extract()
        if widget_value is not null:
            self.value = widget_value
            return

        # Step 1.2: get from content
        if value is null:
            if self.content is not null:
                value = self.content

            # Step 1.2.2: default
            if value is null:
                value = self.default

        # Step 1.4: Convert the value to one that the widget can understand
        if value is not null:
            self.value = self.serialize(value)

    def serialize(self, value):
        raise NotImplemented

    def deserialize(self, value):
        raise NotImplemented

    def validate(self, value):
        if value is required:
            raise Invalid(self, _('Required'))

        if self.validator is not None:
            self.validator(self, value)

    def extract(self, default=null):
        value = self.params.get(self.name, default)
        if not value:
            return null
        return value

    def render(self, request):
        try:
            if self.mode == FORM_DISPLAY:
                return self.tmpl_display(
                    view = view,
                    context = self,
                    request = self.request)
            else:
                return self.tmpl_input(
                    view = self,
                    context = self,
                    request = self.request)
        except:
            import traceback
            traceback.print_exc()

    def addClass(self, klass):
        if not self.klass:
            self.klass = klass
        else:
            if klass not in self.klass:
                self.klass = u'%s %s'%(self.klass, klass)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class SequenceField(Field):
    """ sequence field """

    value = ()
    terms = None
    empty_marker = ''

    noValueToken = '--NOVALUE--'

    @property
    def displayValue(self):
        value = []
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.noValueToken:
                continue
            term = self.terms.getTermByToken(token)
            if ITerm.providedBy(term):
                value.append(self.localizer.translate(term.title))
            else:
                value.append(term.value)
        return value

    def updateTerms(self):
        if self.terms is None:
            self.terms = getattr(self.node, 'vocabulary', None)
            if self.terms is None:
                self.terms = config.registry.getMultiAdapter(
                    (self.node, self.typ, self), IVocabulary)

        return self.terms

    def update(self, request):
        self.empty_marker = '%s-empty-marker'%self.name

        # Create terms first, since we need them for the generic update.
        self.updateTerms()
        super(SequenceField, self).update(request)

    def extract(self, default=null):
        if (self.name not in self.params and
            self.empty_marker in self.params):
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


class FieldFactory(Field):

    __field__ = ''

    def __init__(self, typ, name, **kw):
        self.__field__ = typ

        super(FieldFactory, self).__init__(name, **kw)

    def bind(self, prefix, content, params):
        cls = getField(self.__field__)
        if cls is None:
            raise TypeError(
                "Can't find field implementation for '%s'"%cls.__field__)

        clone = cls.__new__(cls)
        clone.__dict__.update(self.__dict__)
        clone.content = content
        clone.params = params
        clone.name = '%s%s'%(prefix, self.name)
        return clone
