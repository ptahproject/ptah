""" schemas """
import colander
from zope.component import getUtility
from ptah.interfaces import _, IPasswordTool
from ptah.models import User

def lower(s):
    if isinstance(s, basestring):
        return s.lower()
    return s

def checkLogin(node, login):
    if login and User.get(login) is not None:
        raise colander.Invalid(node, _('Login already is in use.'))


class RegistrationSchema(colander.Schema):

    fullname = colander.SchemaNode(
        colander.Str(),
        title=_('Full Name'),
        description=_(u"e.g. John Smith. This is how users "
                      u"on the site will identify you."),
        )

    login = colander.SchemaNode(
        colander.Str(),
        title = _(u'E-mail/Login'),
        description = _(u'This is the username you will use to log in. '
                        'It must be an email address. <br /> Your email address '
                        'will not be displayed to any user or be shared with '
                        'anyone else.'),
        preparer = lower,
        validator = colander.All(colander.Email(), checkLogin),
        )


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
        default = u'')



class ResetPasswordSchema(colander.Schema):
    """ reset password """

    login = colander.SchemaNode(
        colander.Str(),
        title = _(u'Login Name'),
        description = _('Login names are not case sensitive.'),
        missing = u'',
        default = u'')



def passwordSchemaValidator(node, appstruct):
    if appstruct['password'] and appstruct['confirm_password']:
        if appstruct['password'] != appstruct['confirm_password']:
            raise colander.Invalid(
                node, _("Password and Confirm Password should be the same."))

        err = getUtility(IPasswordTool).validatePassword(appstruct['password'])
        if err is not None:
            raise colander.Invalid(node, err)


PasswordSchema = colander.SchemaNode(
    colander.Mapping(),
    
    colander.SchemaNode(
        colander.Str(),
        name = 'password',
        title = _(u'New password'),
        description = _(u'Enter new password. '\
                        u'No spaces or special characters, should contain '\
                        u'digits and letters in mixed case.'),
        default = u''),

    colander.SchemaNode(
        colander.Str(),
        name = 'confirm_password',
        title = _(u'Confirm password'),
        description = _(u'Re-enter the password. '
                        u'Make sure the passwords are identical.'),
        default = u''),

    validator = passwordSchemaValidator
)


"""
class SChangePasswordForm(interface.Interface):

    current_password = CurrentPassword(
        title = _(u'Current password'),
        description = _(u'Enter your current password.'),
        missing_value = u'',
        required = True)
"""
