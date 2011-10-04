from collections import OrderedDict
from pyramid.i18n import get_localizer

from memphis import config
from memphis.form.error import Invalid
from memphis.form.interfaces import \
    IForm, IField, IWidget, IWidgets, IDataManager, null, required
from memphis.form.interfaces import _, FORM_INPUT, FORM_DISPLAY


class Fieldset(OrderedDict):

    def __init__(self, *args, **kwargs):
        super(Fieldset, self).__init__()

        name = kwargs.pop('name', u'')
        legend = kwargs.pop('legend', u'')

        self.name = name
        self.legend = legend
        self.names = []
        self.schemas = []
        self.prefix = '%s.'%self.name if self.name else ''
        self.lprefix = len(self.prefix)

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

    def unflatten(self, appdata):
        data = dict((key[self.lprefix:], appdata[key])
                    for key in appdata if key in self.names)

        for name, fieldset in self.items():
            if isinstance(fieldset, Fieldset):
                data[name] = fieldset.unflatten(appdata)

        return data

    def append(self, *args, **kwargs):
        omit = kwargs.get('omit', ())
        select = kwargs.get('select', ())

        for field in args:
            if isinstance(field, Field):
                if field.name in self:
                    raise ValueError("Duplicate name", field.name)
                self[field.name] = field
                self.names.append('%s%s'%(self.prefix, field.name))

            elif isinstance(field, Fieldset):
                if field.name in self:
                    raise ValueError("Duplicate name", field.name)
                self[field.name] = field
                self.names.append('%s%s'%(self.prefix, field.name))

            else:
                pass
                #raise TypeError("Unrecognized argument type", field)

    def select(self, *names):
        return self.__class__(select=names, *self.schemas)

    def omit(self, *names):
        return self.__class__(omit=names, *self.schemas)

    def validator(self, node, appstruct):
        for schema in self.schemas:
            if schema.validator is not None:
                schema.validator(schema, appstruct)


class Field(object):
    """Widget base class."""

    name = ''
    label = u''
    description = u''
    required = False

    error = None
    content = None
    params = {}
    localizer = None
    value = null
    mode = FORM_INPUT

    tmpl_input = None
    tmpl_display = None

    def __init__(self, name, **kw):
        self.name = name
        self.label = kw.get('title', name.capitalize())
        self.description = kw.get('description', u'')
        self.readonly = kw.get('readonly', None)
        self.missing = kw.get('missing', required)
        self.default = kw.get('missing', null)
        self.validator = kw.get('validator', None)

    @property
    def required(self):
        return self.missing is required

    def bind(self, content, params, request, **kw):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.content = content
        clone.params = params
        clone.request = request
        clone.localizer = kw.get('localizer')
        mode = kw.get('mode')
        if mode:
            clone.mode = mode
        elif self.readonly:
            clone.mode = FORM_DISPLAY

        value = null

        # Step 1.1: If possible, get a value from the params
        widget_value = self.extract(params)
        if widget_value is not null:
            clone.value = widget_value
            return clone

        # Step 1.2: If we have a widget with a field and we have no value yet,
        #           we have some more possible locations to get the value
        if value is null:
            # Step 1.2.1: If the widget knows about its content and the
            #              content is to be used to extract a value, get
            #              it now via a data manager.
            if content is not None:
                value = content.query(self)

            # Step 1.2.2: If we still do not have a value, we can always use
            #             the default value of the node, id set
            if ((value is self.missing or value is null) and
                self.default is not null):
                value = self.default

        # Step 1.4: Convert the value to one that the widget can understand
        if value is not null:
            clone.value = self.serialize(value)

        return clone

    def deserialize(self, value):
        if value is null:
            value = self.missing
            if value is required:
                raise Invalid(self, _('Required'))
            return value

        if self.validator is not None:
            self.validator(self, value)
        return value

    def extract(self, params, default = null):
        value = params.get(self.name, default)
        if not value:
            return null
        return value

    def render(self, request):
        if self.mode == FORM_DISPLAY:
            return self.tmpl_display(
                context = self,
                request = self.request)
        else:
            return self.tmpl_input(
                context = self,
                request = self.request)

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

    def update(self):
        self.empty_marker = '%s-empty-marker'%self.name

        # Create terms first, since we need them for the generic update.
        self.updateTerms()
        super(SequenceWidget, self).update()

    def extract(self, params, default=null):
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

        if value is not default and \
                not isinstance(self.node.typ, Positional):
            if value:
                return value[0]
            else:
                return default

        return value
