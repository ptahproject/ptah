""" schemas """
import colander
from zope.component import getUtility
from ptah.security import passwordTool

from interfaces import _
from provider import CrowdUser


def lower(s):
    if isinstance(s, basestring):
        return s.lower()
    return s


def checkLogin(node, login):
    if login and CrowdUser.get(login) is not None:
        raise colander.Invalid(node, _('Login already is in use.'))


def passwordValidator(node, appstruct):
    err = passwordTool.validatePassword(appstruct)
    if err is not None:
        raise colander.Invalid(node, err)


class RegistrationSchema(colander.Schema):

    name = colander.SchemaNode(
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


class ResetPasswordSchema(colander.Schema):
    """ reset password """

    login = colander.SchemaNode(
        colander.Str(),
        title = _(u'Login Name'),
        description = _('Login names are not case sensitive.'),
        missing = u'',
        default = u'')


class UserSchema(colander.Schema):

    id = colander.SchemaNode(
        colander.Int(),
        title=_('Id'))

    name = colander.SchemaNode(
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

    password = colander.SchemaNode(
        colander.Str(),
        title = _(u'New password'),
        description = _(u'Enter new password. '\
                        u'No spaces or special characters, should contain '\
                        u'digits and letters in mixed case.'),
        validator = passwordValidator)


class ManagerChangePasswordSchema(colander.Schema):

    password = colander.SchemaNode(
        colander.Str(),
        title = _(u'New password'),
        description = _(u'Enter new password. '\
                        u'No spaces or special characters, should contain '\
                        u'digits and letters in mixed case.'),
        validator = passwordValidator)
