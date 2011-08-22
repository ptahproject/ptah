""" schemas """
import colander
from memphis.users.interfaces import _


class RegistrationSchema(colander.SchemaNode):
    pass

"""
    firstname = schema.TextLine(
    title=_('First Name'),
    description=_(u"e.g. John. This is how users "
                      u"on the site will identify you."),
        required = True,
        )

    lastname = schema.TextLine(
        title=_('Last Name'),
        description=_(u"e.g. Smith. This is how users "
                      u"on the site will identify you."),
        required = True)

    #login = NewLoginField(
    #    title = _(u'E-mail/Login'),
    #    description = _(u'This is the username you will use to log in. '\
    #        'It must be an email address. <br /> Your email address will not '\
    #'be displayed to any user or be shared with anyone else.'),
    #    required = True)
"""


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
    """ reset password form """

    login = colander.SchemaNode(
        colander.Str(),
        title = _(u'Login Name'),
        description = _('Login names are case sensitive, '\
                            'make sure the caps lock key is not enabled.'),
        default = u'')


class PasswordSchema(colander.Schema):
    
    password = colander.SchemaNode(
        colander.Str(),
        title = _(u'New password'),
        description = _(u'Enter new password. '\
                        u'No spaces or special characters, should contain '\
                        u'digits and letters in mixed case.'),
        default = u'')

    confirm_password = colander.SchemaNode(
        colander.Str(),
        title = _(u'Confirm password'),
        description = _(u'Re-enter the password. '
                        u'Make sure the passwords are identical.'),
        default = u'')


"""
class SChangePasswordForm(interface.Interface):

    current_password = CurrentPassword(
        title = _(u'Current password'),
        description = _(u'Enter your current password.'),
        missing_value = u'',
        required = True)
"""
