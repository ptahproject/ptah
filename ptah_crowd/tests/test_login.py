import transaction
import ptah, ptah_crowd
from memphis import config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound

from base import Base


class TestSuspended(Base):

    def test_suspended_anon(self):
        from ptah_crowd import login

        request = DummyRequest()
        view = login.LoginSuspended(None, request)
        self.assertRaises(HTTPFound, view.update)

    def test_suspended_not(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.uri
        props = ptah_crowd.get_properties(uri)
        props.suspended = False
        transaction.commit()

        request = DummyRequest()
        ptah.authService.set_userid(uri)

        res = login.LoginSuspended.__renderer__(None, request)
        self.assertIsInstance(res, HTTPFound)

    def test_suspended(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        uri = user.uri

        props = ptah_crowd.get_properties(uri)
        props.suspended = True

        ptah.authService.set_userid(user.uri)

        request = DummyRequest()
        res = login.LoginSuspended.__renderer__(None, request).body
        
        self.assertIn('Your account is suspended', res)


class TestLogout(Base):

    def test_logout_anon(self):
        from ptah_crowd import login

        request = DummyRequest()
        self.assertRaises(HTTPFound, login.logout, request)

    def test_logout(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.uri
        Session.add(user)
        Session.flush()
        transaction.commit()

        request = DummyRequest()
        ptah.authService.set_userid(uri)

        try:
            login.logout(request)
        except Exception, res:
            pass
        
        self.assertIsInstance(res, HTTPFound)
        self.assertIsNone(ptah.authService.get_userid())


class TestLogoutSuccess(Base):

    def test_login_success_anon(self):
        from ptah_crowd import login

        request = DummyRequest()

        res = login.LoginSuccess.__renderer__(None, request)

        self.assertEqual(
            res.headers['location'], 'http://example.com/login.html')

    def test_login_success(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.uri
        Session.add(user)
        Session.flush()
        transaction.commit()

        request = DummyRequest()
        ptah.authService.set_userid(uri)

        res = login.LoginSuccess.__renderer__(None, request).body
        self.assertIn('You are now logged in', res)
