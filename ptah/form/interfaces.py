""" Form and Field Interfaces """
from zope import interface
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request
from translationstring import TranslationStringFactory

MessageFactory = _ = TranslationStringFactory('ptah.form')


class Invalid(Exception):
    """An exception raised by data types and validators indicating that
    the value for a particular field was not valid.

    ``msg``: Error message

    ``field``: Field object

    ``mapping``: Mapping for translate message interpolation

    ``name``: Custom error name

    ``errors``: Sub errors
    """

    def __init__(self, msg='', field=None, mapping=None, name=None,errors=None):
        self.msg = msg
        self.field = field
        self.mapping = mapping
        self.name = name

        self.errors = {}

        if errors:
            for err in errors:
                self[err.name] = err

    def __str__(self):
        request = getattr(self.field, 'request', None)
        if request is None:
            request = get_current_request()

        if request is None:
            return self.msg

        return get_localizer(request).translate(self.msg, mapping=self.mapping)

    def __repr__(self):
        return 'Invalid(%s: %s)' % (self.field or self.name or '', self.msg)

    def __contains__(self, name):
        """ Check for subexception """
        return name in self.errors

    def __setitem__(self, name, err):
        """ Add a subexception """
        err.name = name
        self.errors[name] = err

    def __getitem__(self, name):
        """ Get a subexception by name """
        return self.errors[name]

    def get(self, name, default=None):
        """ Get a subexception by name """
        return self.errors.get(name)


class _null(object):
    """ Represents a null value in field-related operations. """

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return True
        return False

    def __len__(self):
        return 0

    def __nonzero__(self):
        return False

    __bool__ = __nonzero__

    def __repr__(self):
        return '<widget.null>'

null = _null()


class HTTPResponseIsReady(Exception):
    """ An exception raised by form update method indicates
    form should return http response """


# ----[ Vocabulary ]----------------------------------------------------------

# vocabulary/term interfaces
class ITerm(interface.Interface):
    """ term """

    value = interface.Attribute('Value')
    token = interface.Attribute('Token')
    title = interface.Attribute('Title')


class IVocabulary(interface.Interface):
    """ vocabulary """

    def get_term(value):
        """Return an ITitledTokenizedTerm object for the given value

        LookupError is raised if the value isn't in the source
        """

    def get_term_bytoken(token):
        """Return an ITokenizedTerm for the passed-in token.

        If `token` is not represented in the vocabulary, `LookupError`
        is raised.
        """

    def get_value(token):
        """Return a value for a given identifier token

        LookupError is raised if there isn't a value in the source.
        """

    def __iter__():
        """Iterate over terms."""

    def __len__():
        """Return number of terms."""

    def __contains__(value):
        """Check wether terms containes the ``value``."""

# --- API ---

def Validator(field, value):
    """
    A validator is called during field value validation.

    If ``value`` is not valid, raise a :class:`ptah.form.Invalid`
    instance as an exception after.

    ``field`` is a :class:`ptah.form.Field` instance, for use when
    raising a :class:`ptah.form.Invalid` exception.
    """


def Preview(request):
    """
    A preview is called by ``Field types`` management module.

    :param request: Pyramid request object
    :rtype: Html snippet
    """


def VocabularyFactory(context):
    """ :class:`ptah.form.fields.VocabularyField` instantiate vocabulary
    during field binding process.

    :param context: Field context
    :rtype: Vocabulary instance
    """
