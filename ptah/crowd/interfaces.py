""" crowd interfaces """
import ptah
import translationstring
from zope import interface
from memphis import config

_ = translationstring.TranslationStringFactory('ptah')


class PrincipalEvent(object):

    principal = interface.Attribute('Principal object')

    def __init__(self, principal):
        self.principal = principal


class LoggedInEvent(PrincipalEvent):
    """ User logged in to system."""
    config.event('Logged in event')


class LogingFailedEvent(object):
    """ User loging failed."""
    config.event('Loging failed event')

    login = interface.Attribute('Login')

    def __init__(self, login):
        self.login = login


class ResetPasswordInitiatedEvent(PrincipalEvent):
    """ User has initiated password changeing."""
    config.event('Reset password initiated event')


class ValidatedEvent(PrincipalEvent):
    """ User account has been validated."""
    config.event('Account validation event')


class UserAddedEvent(PrincipalEvent):
    """ """

    user = interface.Attribute('User object')


class UserRegisteredEvent(UserAddedEvent):
    """ """


class ICrowdModule(ptah.IPtahModule):
    """ marker interface for crowd module """


class ICrowdUser(interface.Interface):
    """ wrapper for actual user """

    user = interface.Attribute('Wrapped user object')


class IPreferencesPanel(interface.Interface):
    """ preferences panel """


class IAction(interface.Interface):
    """ ptah action """

    title = interface.Attribute('User friendly title')

    action = interface.Attribute('Action')

    def available(principal):
        """ check if action is availble for principal """


class IManageUserAction(IAction):
    """ user management action """


class IPersonalAction(IAction):
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


class IPreferencesGroup(interface.Interface):
    """ preferences group """

    id = interface.Attribute('Unique pref id')

    schema = interface.Attribute('Colander schema')

    def get(id):
        """ Return preferences for principal.

        method returns dictionary. """

    def update(id, **kwargs):
        """ update preferences """
