""" interfaces """
import translationstring
from zope import interface

_ = translationstring.TranslationStringFactory('ptah')


AUTH_RESETPWD = 1


class IAuthentication(interface.Interface):
    """ authentication service """

    def isAnonymous():
        """ check if current use is anonymous """

    def authenticate(credentials):
        """ authenticate credentials """

    def getUserByLogin(login):
        """ return user by login """


class IUser(interface.Interface):
    """ user behavior """


class IUserInfo(interface.Interface):
    pass

    #fullname = schema.TextLine(
    #    title = u'Fullname',
    #    required = True)

    #login = schema.TextLine(
    #    title = u'Login',
    #    required = True)

    #password = schema.TextLine(
    #    title = u'Password',
    #    required = True)

    #confirmed = schema.Bool(
    #    title = u'Confirmed',
    #    required = False)


class IPasswordTool(interface.Interface):
    """ password tool """

    #min_length = schema.Int(
    #    title = _(u'Minimum length'),
    #    description = _(u'Minimun length of password.'),
    #    default = 5,
    #    required = True)

    #letters_digits = schema.Bool(
    #    title = _(u'Letters and digits'),
    #    description = _(u'Password should contain both letters and digits.'),
    #    default = False,
    #    required = True)

    #letters_mixed_case = schema.Bool(
    #    title = _(u'Letters case'),
    #    description = _(u'Password should contain letters in mixed case.'),
    #    default = False,
    #    required = True)

    def encodePassword(password, *args, **kw):
        """ encode password """

    def checkPassword(encodedPassword, password):
        """ check password """

    def validatePassword(password):
        """ validate password """

    def passwordStrength(password):
        """ check password strength """

    def getPasscode(pid):
        """ return passcode by principal """

    def getPrincipal(passcode):
        """ return principal by passcode """

    def generatePasscode(principal):
        """ generate passcode for principal """

    def resetPassword(passcode, password):
        """ reset password """


class IPasswordReset(interface.Interface):
    pass

    #storage.schema('memphis.user:resetpassword')

    #passcode = schema.TextLine(
    #    title = u'Reset password code',
    #    required = True)


class IPtahRoute(interface.Interface):
    """ ptah route """
