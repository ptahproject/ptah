""" schemas """
import colander
from interfaces import _


class LoginSchema(colander.Schema):
    """ login form """

    login = colander.SchemaNode(
        colander.Str(),
        title = _(u'Login Name'),
        description = _('Login names are case sensitive, '\
                            'make sure the caps lock key is not enabled.'),
        default = u'')

    password = colander.SchemaNode(
        colander.Str(),
        title = _(u'Password'),
        description = _('Case sensitive, make sure caps lock is not enabled.'),
        default = u'',
        widget = 'password')



class ResetPasswordSchema(colander.Schema):
    """ reset password """

    login = colander.SchemaNode(
        colander.Str(),
        title = _(u'Login Name'),
        description = _('Login names are not case sensitive.'),
        missing = u'',
        default = u'')


PasswordSchema = colander.SchemaNode(
    colander.Mapping(),

    colander.SchemaNode(
        colander.Str(),
        name = 'password',
        title = _(u'Password'),
        description = _(u'Enter password. '\
                        u'No spaces or special characters, should contain '\
                        u'digits and letters in mixed case.'),
        default = u'',
        widget = 'password'),

    colander.SchemaNode(
        colander.Str(),
        name = 'confirm_password',
        title = _(u'Confirm password'),
        description = _(u'Re-enter the password. '
                        u'Make sure the passwords are identical.'),
        default = u'',
        widget = 'password'),

    #validator = passwordSchemaValidator
)
