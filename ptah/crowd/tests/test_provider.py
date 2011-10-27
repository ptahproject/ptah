""" role """
import transaction
import ptah, ptah.crowd
from ptah import config

from base import Base


class TestProvider(Base):

    def test_authenticate(self):
        from ptah.crowd.provider import CrowdProvider, CrowdUser, Session

        provider = CrowdProvider()

        self.assertFalse(
            provider.authenticate(
                {'login': 'test', 'password': '12345'}))

        user = CrowdUser('test', 'test', 'test@ptahproject.org',
                         ptah.passwordTool.encode('12345'))
        Session.add(user)
        transaction.commit()

        self.assertTrue(
            provider.authenticate(
                {'login': 'test', 'password': '12345'}))

        self.assertFalse(
            provider.authenticate(
                {'login': 'test', 'password': '56789'}))


    def test_get_bylogin(self):
        from ptah.crowd.provider import CrowdProvider, CrowdUser, Session

        provider = CrowdProvider()

        self.assertIsNone(provider.get_principal_bylogin('test'))

        user = CrowdUser('test', 'test', 'test@ptahproject.org',
                         ptah.passwordTool.encode('12345'))
        Session.add(user)
        transaction.commit()

        user = provider.get_principal_bylogin('test')
        self.assertIsInstance(user, CrowdUser)
        self.assertEqual(user.login, 'test')

    def test_crowd_user_ctor(self):
        from ptah.crowd.provider import CrowdUser

        user = CrowdUser('user-name', 'user-login', 'user-email', 'passwd')

        self.assertEqual(user.name, 'user-name')
        self.assertEqual(user.login, 'user-login')
        self.assertEqual(user.email, 'user-email')
        self.assertEqual(user.password, 'passwd')
        self.assertTrue(user.uri.startswith('user-crowd'))
        self.assertEqual(str(user), 'user-name')
        self.assertEqual(repr(user), 'CrowdUser<%s:%s>'%(user.name, user.uri))

    def test_crowd_user_get(self):
        from ptah.crowd.provider import CrowdUser, Session

        user = CrowdUser('user-name', 'user-login', 'user-email', 'passwd')
        uri = user.uri

        Session.add(user)
        Session.flush()

        self.assertEqual(CrowdUser.get(user.pid).uri, uri)
        self.assertEqual(CrowdUser.get_byuri(user.uri).uri, uri)
        self.assertEqual(CrowdUser.get_bylogin(user.login).uri, uri)

    def test_crowd_user_change_password(self):
        from ptah.crowd.provider import CrowdUser, change_pwd

        user = CrowdUser('user-name', 'user-login', 'user-email', 'passwd')
        uri = user.uri

        change_pwd(user, '123456')
        self.assertEqual(user.password, '123456')

    def test_crowd_user_change_search(self):
        from ptah.crowd.provider import Session, CrowdUser, search

        user = CrowdUser('user-name', 'user-login', 'user-email', 'passwd')
        uri = user.uri

        Session.add(user)
        Session.flush()

        users = list(search('user'))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].uri, uri)

        users = list(search('email'))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].uri, uri)
