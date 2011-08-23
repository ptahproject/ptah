""" crowd interfaces """
import ptah
import translationstring
from zope import interface

_ = translationstring.TranslationStringFactory('ptah')


class ICrowdModule(ptah.IPtahModule):
    """ marker interface for crowd module """


class ICrowdUser(interface.Interface):
    """ wrapper for actual user """

    user = interface.Attribute('Wrapped user object')


class IAction(interface.Interface):
    """ ptah action """

    title = interface.Attribute('User friendly title')
    
    action = interface.Attribute('Action')


class IManageAction(IAction):
    """ management action """

    def available():
        """ check if action is availble for principal """


class IUserAction(IAction):

    def available(principal):
        """ check if action is availble for principal """


class IManageUserAction(IUserAction):
    """ user management action """


class IPersonalAction(IUserAction):
    """ user preferences action """


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
