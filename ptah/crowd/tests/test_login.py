import transaction
import ptah
from ptah import config, crowd
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound

from base import Base


class TestSuspended(Base):

    def test_suspended_anon(self):
        from ptah.crowd import login

        request = DummyRequest()
        view = login.LoginSuspended(None, request)
        self.assertRaises(HTTPFound, view.update)

    def test_suspended_not(self):
        from ptah.crowd import login
        from ptah.crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.uri
        props = ptah.crowd.get_properties(uri)
        props.suspended = False
        transaction.commit()

        request = DummyRequest()
        ptah.authService.set_userid(uri)

        res = login.LoginSuspended.__renderer__(None, request)
        self.assertIsInstance(res, HTTPFound)

    def test_suspended(self):
        from ptah.crowd import login
        from ptah.crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        uri = user.uri

        props = ptah.crowd.get_properties(uri)
        props.suspended = True

        ptah.authService.set_userid(user.uri)

        request = DummyRequest()
        res = login.LoginSuspended.__renderer__(None, request).body

        self.assertIn('Your account is suspended', res)


class TestLogout(Base):

    def test_logout_anon(self):
        from ptah.crowd import login

        request = DummyRequest()
        self.assertRaises(HTTPFound, login.logout, request)

    def test_logout(self):
        from ptah.crowd import login
        from ptah.crowd.provider import CrowdUser, Session

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
        from ptah.crowd import login

        request = DummyRequest()

        res = login.LoginSuccess.__renderer__(None, request)

        self.assertEqual(
            res.headers['location'], 'http://example.com/login.html')

    def test_login_success(self):
        from ptah.crowd import login
        from ptah.crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.uri
        Session.add(user)
        Session.flush()
        transaction.commit()

        request = DummyRequest()
        ptah.authService.set_userid(uri)

        res = login.LoginSuccess.__renderer__(None, request).body
        self.assertIn('You are now logged in', res)


class TestLogin(Base):

    def test_login_auth(self):
        from ptah.crowd import login

        request = DummyRequest()

        ptah.authService.set_userid('test')
        res = login.LoginForm.__renderer__(None, request)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(
            res.headers['location'],
            'http://example.com/login-success.html')

    def test_login_update(self):
        from ptah.crowd import login

        request = DummyRequest()

        ptah.crowd.CONFIG['join'] = False
        ptah.crowd.CONFIG['joinurl'] = 'http://test/login.html'

        form = login.LoginForm(None, request)
        form.update()
        self.assertFalse(form.join)
        self.assertEqual(form.joinurl, 'http://test/login.html')

        res = login.LoginForm.__renderer__(None, request).body
        self.assertNotIn('head over to the registration form', res)

    def test_login_update_join(self):
        from ptah.crowd import login

        request = DummyRequest()

        ptah.crowd.CONFIG['join'] = True
        ptah.crowd.CONFIG['joinurl'] = ''

        form = login.LoginForm(None, request)
        form.update()
        self.assertTrue(form.join)
        self.assertEqual(form.joinurl, 'http://example.com/join.html')

        res = login.LoginForm.__renderer__(None, request).body
        self.assertIn('head over to the registration form', res)

    def test_login(self):
        from ptah.crowd import login
        from ptah.crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'login', 'email',
                         password = '{plain}12345')
        uri = user.uri
        Session.add(user)
        Session.flush()
        transaction.commit()

        request = DummyRequest()

        form = login.LoginForm(None, request)
        form.update()
        data, errors = form.extract()
        self.assertEqual(len(errors), 2)

        form.handleLogin()
        self.assertIn('Please fix indicated errors.',
                      request.session['msgservice'][0])

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'})

        form = login.LoginForm(None, request)
        form.update()
        data, errors = form.extract()

        try:
            form.handleLogin()
        except Exception, res:
            pass

        self.assertEqual(res.headers['location'],
                         'http://example.com/login-success.html')

    def test_login_wrong_login(self):
        from ptah.crowd import login
        from ptah.crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'login', 'email',
                         password = '{plain}12345')
        uri = user.uri
        Session.add(user)
        Session.flush()
        transaction.commit()

        request = DummyRequest(
            POST={'login': 'login1', 'password': '123456'})

        form = login.LoginForm(None, request)
        form.update()
        form.handleLogin()

        self.assertIn('You enter wrong login or password',
                      request.session['msgservice'][0])

    def test_login_unvalidated(self):
        from ptah.crowd import login
        from ptah.crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'login', 'email',
                         password = '{plain}12345')
        uri = user.uri
        Session.add(user)
        ptah.crowd.get_properties(uri).validated = False
        transaction.commit()

        ptah.crowd.CONFIG['allow-unvalidated'] = False

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'})

        form = login.LoginForm(None, request)
        form.update()
        form.handleLogin()

        self.assertIn('Account is not validated.',
                      request.session['msgservice'][0])

    def test_login_suspended(self):
        from ptah.crowd import login
        from ptah.crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'login', 'email',
                         password = '{plain}12345')
        uri = user.uri
        Session.add(user)
        ptah.crowd.get_properties(uri).suspended = True
        transaction.commit()

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'})

        form = login.LoginForm(None, request)
        form.update()
        try:
            form.handleLogin()
        except Exception, res:
            pass

        self.assertEqual(res.headers['location'],
                         'http://example.com/login-suspended.html')
