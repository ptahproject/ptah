""" schemas """
import ptah
from ptah import form
from ptah.password import passwordValidator

from settings import _


def lower(s):
    if isinstance(s, basestring):
        return s.lower()
    return s


def checkLoginValidator(node, login):
    if getattr(node, 'content', None) == login:
        return

    if ptah.authService.get_principal_bylogin(login) is not None:
        raise form.Invalid(node, _('Login already is in use.'))


RegistrationSchema = form.Fieldset(

    form.TextField(
        'name',
        title=_('Full Name'),
        description=_(u"e.g. John Smith. This is how users "
                      u"on the site will identify you."),
        ),

    form.TextField(
        'login',
        title = _(u'E-mail/Login'),
        description = _(u'This is the username you will use to log in. '
                        'It must be an email address. <br /> Your email address '
                        'will not be displayed to any user or be shared with '
                        'anyone else.'),
        preparer = lower,
        validator = form.All(form.Email(), checkLoginValidator),
        )
    )


ResetPasswordSchema = form.Fieldset(

    form.TextField(
        'login',
        title = _(u'Login Name'),
        description = _('Login names are not case sensitive.'),
        missing = u'',
        default = u'')
    )


UserSchema = form.Fieldset(

    form.fields.TextField(
        'name',
        title=_('Full Name'),
        description=_(u"e.g. John Smith. This is how users "
                      u"on the site will identify you."),
        ),

    form.fields.TextField(
        'login',
        title = _(u'E-mail/Login'),
        description = _(u'This is the username you will use to log in. '
                        'It must be an email address. <br /> Your email address '
                        'will not be displayed to any user or be shared with '
                        'anyone else.'),
        preparer = lower,
        validator = form.All(form.Email(), checkLoginValidator),
        ),

    form.fields.TextField(
        'password',
        title = _(u'Password'),
        description = _(u'Enter password. '\
                        u'No spaces or special characters, should contain '\
                        u'digits and letters in mixed case.'),
        validator = passwordValidator),

    form.fields.BoolField(
        'validated',
        title = _(u'Validated'),
        default = True,
        ),

    form.fields.BoolField(
        'suspended',
        title = _(u'Suspended'),
        default = False,
        ),

    )


ManagerChangePasswordSchema = form.Fieldset(

    form.PasswordField(
        'password',
        title = _(u'New password'),
        description = _(u'Enter new password. '\
                        u'No spaces or special characters, should contain '\
                        u'digits and letters in mixed case.'),
        validator = passwordValidator)
    )
