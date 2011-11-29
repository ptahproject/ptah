""" Code from `colander` package """
import re
from pyramid.compat import string_types
from ptah.form.interfaces import _, Invalid


class All(object):
    """ Composite validator which succeeds if none of its
    subvalidators raises an :class:`Invalid` exception"""

    def __init__(self, *validators):
        self.validators = list(validators)

    def __call__(self, field, value):
        msgs = []
        for validator in self.validators:
            try:
                validator(field, value)
            except Invalid as e:
                msgs.append(e.msg)

        if msgs:
            raise Invalid(field, msgs)


class Function(object):
    """ Validator which accepts a function and an optional message;
    the function is called with the ``value`` during validation.

    If the function returns anything falsy (``None``, ``False``, the
    empty string, ``0``, an object with a ``__nonzero__`` that returns
    ``False``, etc) when called during validation, an
    :exc:`ptah.form.Invalid` exception is raised (validation fails);
    its msg will be the value of the ``message`` argument passed to
    this class' constructor.

    If the function returns a stringlike object (a ``str`` or
    ``unicode`` object) that is *not* the empty string , a
    :exc:`ptah.form.Invalid` exception is raised using the stringlike
    value returned from the function as the exeption message
    (validation fails).

    If the function returns anything *except* a stringlike object
    object which is truthy (e.g. ``True``, the integer ``1``, an
    object with a ``__nonzero__`` that returns ``True``, etc), an
    :exc:`ptah.form.Invalid` exception is *not* raised (validation
    succeeds).

    The default value for the ``message`` when not provided via the
    constructor is ``Invalid value``.
    """

    def __init__(self, function, message=_('Invalid value')):
        self.function = function
        self.message = message

    def __call__(self, field, value):
        result = self.function(value)

        if not result:
            raise Invalid(field, self.message)

        if isinstance(result, string_types):
            raise Invalid(field, result)


class Regex(object):
    """ Regular expression validator.

        Initialize it with the string regular expression ``regex``
        that will be compiled and matched against ``value`` when
        validator is called. If ``msg`` is supplied, it will be the
        error message to be used; otherwise, defaults to 'String does
        not match expected pattern'.

        The ``regex`` argument may also be a pattern object (the
        result of ``re.compile``) instead of a string.

        When calling, if ``value`` matches the regular expression,
        validation succeeds; otherwise, :exc:`ptah.form.Invalid` is
        raised with the ``msg`` error message.
    """

    def __init__(self, regex, msg=None):
        if isinstance(regex, string_types):
            self.match_object = re.compile(regex)
        else:
            self.match_object = regex
        if msg is None:
            self.msg = _("String does not match expected pattern")
        else:
            self.msg = msg

    def __call__(self, field, value):
        if self.match_object.match(value) is None:
            raise Invalid(field, self.msg)


class Email(Regex):
    """ Email address validator. If ``msg`` is supplied, it will be
        the error message to be used when raising :exc:`ptah.form.Invalid`;
        otherwise, defaults to 'Invalid email address'.
    """

    def __init__(self, msg=None):
        if msg is None:
            msg = _("Invalid email address")

        super(Email, self).__init__(
            '(?i)^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', msg=msg)


class Range(object):
    """ Validator which succeeds if the value it is passed is greater
    or equal to ``min`` and less than or equal to ``max``.  If ``min``
    is not specified, or is specified as ``None``, no lower bound
    exists.  If ``max`` is not specified, or is specified as ``None``,
    no upper bound exists.

    ``min_err`` is used to form the ``msg`` of the
    :exc:`ptah.form.Invalid` error when reporting a validation failure
    caused by a value not meeting the minimum.  If ``min_err`` is
    specified, it must be a string.  The string may contain the
    replacement targets ``${min}`` and ``${val}``, representing the
    minimum value and the provided value respectively.  If it is not
    provided, it defaults to ``'${val} is less than minimum value
    ${min}'``.

    ``max_err`` is used to form the ``msg`` of the
    :exc:`ptah.form.Invalid` error when reporting a validation failure
    caused by a value exceeding the maximum.  If ``max_err`` is
    specified, it must be a string.  The string may contain the
    replacement targets ``${max}`` and ``${val}``, representing the
    maximum value and the provided value respectively.  If it is not
    provided, it defaults to ``'${val} is greater than maximum value
    ${max}'``.
    """
    min_err = _('${val} is less than minimum value ${min}')
    max_err = _('${val} is greater than maximum value ${max}')

    def __init__(self, min=None, max=None, min_err=None, max_err=None):
        self.min = min
        self.max = max
        if min_err is not None:
            self.min_err = min_err
        if max_err is not None:
            self.max_err = max_err

    def __call__(self, field, value):
        if self.min is not None:
            if value < self.min:
                min_err = _(self.min_err,
                            mapping={'val': value, 'min': self.min})
                raise Invalid(field, min_err)

        if self.max is not None:
            if value > self.max:
                max_err = _(self.max_err,
                            mapping={'val': value, 'max': self.max})
                raise Invalid(field, max_err)


class Length(object):
    """ Validator which succeeds if the value passed to it has a
    length between a minimum and maximum.  The value is most often a
    string."""

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, field, value):
        if self.min is not None:
            if len(value) < self.min:
                min_err = _('Shorter than minimum length ${min}',
                            mapping={'min': self.min})
                raise Invalid(field, min_err)

        if self.max is not None:
            if len(value) > self.max:
                max_err = _('Longer than maximum length ${max}',
                            mapping={'max': self.max})
                raise Invalid(field, max_err)


class OneOf(object):
    """ Validator which succeeds if the value passed to it is one of
    a fixed set of values """

    def __init__(self, choices):
        self.choices = choices

    def __call__(self, field, value):
        if not value in self.choices:
            choices = ', '.join(['%s' % x for x in self.choices])
            err = _('"${val}" is not one of ${choices}',
                    mapping={'val': value, 'choices': choices})
            raise Invalid(field, err)
