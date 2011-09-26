""" password tool """
from os import urandom
from random import randint
from codecs import getencoder
from hashlib import sha1
from base64 import urlsafe_b64encode, urlsafe_b64decode
from datetime import timedelta

import colander
from zope import interface
from memphis import config

import ptah
from ptah import token

from settings import PTAH_CONFIG
from interfaces import _, IPasswordTool


TOKEN_TYPE = token.TokenType(
    '35c9b7df958f4e93ae9b275a7dc2219e', timedelta(minutes=10))


class PlainPasswordManager(object):
    """PLAIN password manager."""

    def encode(self, password, salt=None):
        return '{plain}%s'%password

    def check(self, encoded, password):
        if encoded != password:
            return encoded == '{plain}%s'%password
        return True


class SSHAPasswordManager(object):
    """SSHA password manager."""

    _encoder = getencoder("utf-8")

    def encode(self, password, salt=None):
        if salt is None:
            salt = urandom(4)
        hash = sha1(self._encoder(password)[0])
        hash.update(salt)
        return '{ssha}' + urlsafe_b64encode(hash.digest() + salt)

    def check(self, encoded_password, password):
        # urlsafe_b64decode() cannot handle unicode input string. We
        # encode to ascii. This is safe as the encoded_password string
        # should not contain non-ascii characters anyway.
        encoded_password = encoded_password.encode('ascii')
        byte_string = urlsafe_b64decode(encoded_password[6:])
        salt = byte_string[20:]
        return encoded_password == self.encodePassword(password, salt)


class PasswordTool(object):
    """ Password management utility. """
    interface.implements(IPasswordTool)

    min_length = 5
    letters_digits = False
    letters_mixed_case = False

    pm = {'{plain}': PlainPasswordManager(),
          '{ssha}': SSHAPasswordManager(),
          }
    passwordManager = pm['{plain}']

    def __init__(self):
        self._changers = {}

    def checkPassword(self, encodedPassword, password):
        for prefix, pm in self.pm.items():
            if encodedPassword.startswith(prefix):
                return pm.check(encodedPassword, password)

        return self.passwordManager.check(encodedPassword, password)

    def encodePassword(self, password, salt=None):
        return self.passwordManager.encode(password, salt)

    def registerPasswordChanger(self, typ, changer):
        self._changers[typ] = changer

    def hasPasswordChanger(self, uri):
        return ptah.extractUriSchema(uri) in self._changers

    def getPrincipal(self, passcode):
        data = token.service.get(passcode)

        if data is not None:
            return ptah.resolve(data)

    def generatePasscode(self, uri):
        return token.service.generate(TOKEN_TYPE, uri)

    def removePasscode(self, passcode):
        token.service.remove(passcode)

    def changePassword(self, passcode, password):
        principal = self.getPrincipal(passcode)

        self.removePasscode(passcode)

        if principal is not None:
            changer = self._changers.get(ptah.extractUriType(principal.uri))
            if changer is not None:
                changer(principal, self.encodePassword(password))
                return True

        return False

    def validatePassword(self, password):
        if len(password) < self.min_length:
            #return _('Password should be at least ${count} characters.',
            #         mapping={'count': self.min_length})
            return 'Password should be at least %s characters.'%\
                self.min_length
        elif self.letters_digits and \
                (password.isalpha() or password.isdigit()):
            return _('Password should contain both letters and digits.')
        elif self.letters_mixed_case and \
                (password.isupper() or password.islower()):
            return _('Password should contain letters in mixed case.')

    def passwordStrength(self, password):
        return 100.0


passwordTool = PasswordTool()


def passwordSchemaValidator(node, appstruct):
    if appstruct['password'] is colander.required or \
           appstruct['confirm_password'] is colander.required:
        return

    if appstruct['password'] and appstruct['confirm_password']:
        if appstruct['password'] != appstruct['confirm_password']:
            raise colander.Invalid(
                node, _("Password and Confirm Password should be the same."))

        err = passwordTool.validatePassword(appstruct['password'])
        if err is not None:
            raise colander.Invalid(node, err)


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

    validator = passwordSchemaValidator
)


@config.handler(config.SettingsInitializing)
def initializing(ev):
    mng = PasswordTool.pm.get(PTAH_CONFIG.pwdmanager)
    if mng is None:
        mng = PasswordTool.pm.get('{%s}'%PTAH_CONFIG.pwdmanager)

    if mng is None:
        mng = PasswordTool.pm['{plain}']

    passwordTool.passwordManager = mng
