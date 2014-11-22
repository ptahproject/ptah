import logging
from collections import OrderedDict
from ptah.renderer import render
from ptah.form.interfaces import _, null, Invalid

log = logging.getLogger('ptah.form')


class _Field(object):
    """Base class for all fields.

    ``name``: Name of this field.

    ``title``: The title of this field.  Defaults to a titleization
      of the ``name`` (underscores replaced with empty strings and the
      first letter of every resulting word capitalized).  The title is
      used by form for generating html form.

    ``description``: The description for this field.  Defaults to
      ``''`` (the empty string).  The description is used by form.

    ``required``: This value indicates if field is required. By default
      field is required.

    ``validator``: Optional validator for this field.  It should be
      an object that implements the
      :py:class:`ptah.form.interfaces.Validator` interface.

    ``default``: Default field value.

    ``missing``: Field value if value is not specified in bound value.

    ``error``:: Instance os ``ptah.form.interfaces.Invalid`` class or None.

    ``error_msg``:: Custom error message.

    ``tmpl_input``: Pyramid renderer path.

    ``tmpl_widget``: Widget renderer.

    """

    __field__ = ''
    __staticfuncs__ = ('preparer', 'validator')

    name = ''
    title = ''
    description = ''
    flat = False
    preparer = None
    validator = None

    default = null
    required = True
    missing = null

    error = None
    error_msg = ''
    error_required = _('Required')
    error_wrong_type = _('Wrong type')

    request = None
    params = {}
    value = null
    form_value = None
    context = None

    id = None
    typ = None
    readonly = None

    tmpl_input = None
    tmpl_widget = None


    def __init__(self, name=None, **kw):
        self.__dict__.update(kw)

        self.name = name or self.name

    def bind(self, request, prefix, value, params, context=None):
        """ Bind field to value and request params """
        name = '%s%s' % (prefix, self.name)

        return self.cls(
            name = name,
            id = name.replace('.', '-'),
            value = value,
            params = params,
            request = request,
            context = context)

    def set_id_prefix(self, prefix):
        self.id = ('%s%s'%(prefix, self.name)).replace('.', '-')

    def update(self):
        """ Update field, prepare field for rendering """
        # extract from request
        widget_value = self.extract()
        if widget_value is not null:
            self.form_value = widget_value
            return

        # get from value
        if self.value is null:
            value = self.default
        else:
            value = self.value

        # Convert the value to one that the widget can understand
        if value is not null:
            try:
                value = self.to_form(value)
            except Invalid as err:
                value = null
                log.error("Field(%s): %s", self.name, err)

        self.form_value = value if value is not null else None

    def to_form(self, value):
        """ return value representation siutable for html widget """
        return value

    def to_field(self, value):
        """ convert form value to field value """
        return value

    def get_error(self, name=None):
        if name is None:
            return self.error

        if self.error is not None:
            return self.error.get(name)

    def validate(self, value):
        """ validate value """
        if self.required and (value == self.missing or value is null):
            raise Invalid(self.error_required, self)

        if self.typ is not None and not isinstance(value, self.typ):
            raise Invalid(self.error_wrong_type, self)

        if self.validator is not None:
            self.validator(self, value)

    def extract(self):
        """ extract value from params """
        return self.params.get(self.name, null)

    def flatten(self, value):
        """ """
        return {self.name: value}

    def render(self):
        """ render field """
        return render(self.request, self.tmpl_input, self,
                      view=self, value=self.form_value)

    def render_widget(self):
        """ render field widget """
        tmpl = self.tmpl_widget or 'form:widget'
        return render(self.request, tmpl, self,
                      view=self, value=self.form_value)

    def __repr__(self):
        return '%s<%s>' % (self.__class__.__name__, self.name)


# Field metaclass
def _stub_init(self, **kw):
    self.__dict__.update(kw)

def _stub_bind(self, *args, **kw):
    raise TypeError("Can not bind already bound field.")


class _FieldMeta(type):
    """ Construct new class for bind operation """

    def __call__(cls, *args, **kw):
        field = super(_FieldMeta, cls).__call__(*args, **kw)

        field.cls = type(cls.__name__, (cls,), field.__dict__)
        field.cls.__init__ = _stub_init
        field.cls.bind = _stub_bind

        for name in field.__staticfuncs__:
            val = getattr(field, name, None)
            if callable(val):
                setattr(field.cls, name, staticmethod(val))

        return field


# py3 and py3 metaclass support
Field = _FieldMeta('Field', (_Field,), dict(_Field.__dict__))


class InputField(Field):

    klass = 'form-control'

    html_type = 'text'
    html_attrs = ('id', 'name', 'title', 'lang', 'disabled', 'tabindex',
                  'lang', 'disabled', 'readonly', 'alt', 'accesskey',
                  'size', 'maxlength')

    tmpl_input = 'form:input'
    tmpl_display = 'form:input-display'

    def update(self):
        super(InputField, self).update()

        if self.readonly:
            self.add_css_class('disabled')

    def get_html_attrs(self, **kw):
        attrs = OrderedDict()
        attrs['class'] = kw.get('klass', getattr(self, 'klass', None))
        attrs['value'] = kw.get('value', self.form_value)
        for name in self.html_attrs:
            val = getattr(self, name, None)
            attrs[name] = kw.get(name, val)

        return attrs

    def add_css_class(self, css):
        self.klass = ('%s %s' % (self.klass or '', css)).strip()


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

    def bind(self, request, prefix, value, params, context=None):
        try:
            cls = request.registry['ptah.form:field'][self.__field__]
        except KeyError:
            cls = None

        if cls is None:
            raise TypeError(
                "Can't find field implementation for '%s'" % self.__field__)

        clone = cls.__new__(cls)
        clone.__dict__.update(self.__dict__)
        clone.request = request
        clone.value = value
        clone.params = params
        clone.name = '%s%s' % (prefix, self.name)
        clone.id = clone.name.replace('.', '-')
        clone.context = context
        return clone
