""" role """
import transaction
import ptah_crowd
from memphis import config
from ptah.authentication import AuthInfo

from base import Base


class Principal(object):

    def __init__(self, uri, name, login):
        self.uri = uri
        self.name = name
        self.login = login


class TestValidation(Base):

    def test_validation_auth_checker_validation(self):
        from ptah_crowd.validation import validationAndSuspendedChecker
        self._init_memphis()

        principal = Principal('1', 'user', 'user')

        props = ptah_crowd.MemberProperties(principal.uri)
        props.validated = False

        # validation disabled
        info = AuthInfo(True, principal)
        ptah_crowd.CONFIG['validation'] = False
        self.assertTrue(validationAndSuspendedChecker(info))
        transaction.commit()

        info = AuthInfo(True, principal)
        ptah_crowd.CONFIG['allow-unvalidated'] = False
        self.assertTrue(validationAndSuspendedChecker(info))
        transaction.commit()

        # validation enabled
        info = AuthInfo(True, principal)
        ptah_crowd.CONFIG['validation'] = True
        ptah_crowd.CONFIG['allow-unvalidated'] = False
        self.assertFalse(validationAndSuspendedChecker(info))
        self.assertEqual(info.message, 'Account is not validated.')
        transaction.commit()

        info = AuthInfo(True, principal)
        ptah_crowd.CONFIG['allow-unvalidated'] = True
        self.assertTrue(validationAndSuspendedChecker(info))
        transaction.commit()

        # validated
        props = ptah_crowd.MemberProperties(principal.uri)
        props.validated = True
        transaction.commit()

        info = AuthInfo(True, principal)
        ptah_crowd.CONFIG['validation'] = True
        self.assertTrue(validationAndSuspendedChecker(info))

    def test_validation_auth_checker_suspended(self):
        from ptah.authentication import AuthInfo
        from ptah_crowd.validation import validationAndSuspendedChecker
        self._init_memphis()

        principal = Principal('2', 'user', 'user')

        props = ptah_crowd.MemberProperties(principal.uri)
        props.validated = True
        props.suspended = False

        info = AuthInfo(True, principal)
        self.assertTrue(validationAndSuspendedChecker(info))

        props.suspended = True
        info = AuthInfo(True, principal)
        #self.assertFalse(validationAndSuspendedChecker(info))
        #self.assertEqual(info.message, 'Account is suspended.')
