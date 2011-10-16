import transaction
import ptah, ptah_crowd
from memphis import config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from base import Base


class TestJoin(Base):

    def test_join_auth(self):
        from ptah_crowd.registration import Registration

        request = DummyRequest()
        ptah.authService.set_userid('test')

        form = Registration(None, request)
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(
            res.headers['location'], 'http://example.com')

    def test_join_disabled(self):
        from ptah_crowd.registration import Registration

        ptah_crowd.CONFIG['join'] = False

        request = DummyRequest()
        form = Registration(None, request)
        self.assertRaises(HTTPForbidden, form.update)

    def test_join_error(self):
        from ptah_crowd.registration import Registration
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.uri
        Session.add(user)
        Session.flush()

        request = DummyRequest(
            POST = {'name': 'Test user',
                    'login': 'custom login',
                    'password': '12345',
                    'confirm_password': '123456'})

        form = Registration(None, request)
        form.update()

        data, errors = form.extract()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg[0], 'Invalid email address')

        form.register_handler()
        self.assertIn('Please fix indicated errors.',
                      request.session['msgservice'][0])

        request = DummyRequest(
            POST = {'name': 'Test user',
                    'login': 'test@example.com',
                    'password': '12345',
                    'confirm_password': '12345'})
        form = Registration(None, request)
        form.update()
        data, errors = form.extract()
        self.assertEqual(len(errors), 0)

    def test_join(self):
        from ptah_crowd.registration import Registration
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.uri
        Session.add(user)
        Session.flush()

        request = DummyRequest(
            POST = {'name': 'Test user',
                    'login': 'test@example.com',
                    'password': '12345',
                    'confirm_password': '12345'})
        form = Registration(None, request)
        form.update()
        try:
            form.register_handler()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'],
                         'http://example.com/login-success.html')

        user = ptah.authService.get_principal_bylogin('test@example.com')
        self.assertIsInstance(user, CrowdUser)
        self.assertEqual(user.name, 'Test user')

    def test_join_unvalidated(self):
        from ptah_crowd.registration import Registration
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.uri
        Session.add(user)
        Session.flush()

        ptah_crowd.CONFIG['allow-unvalidated'] = False

        request = DummyRequest(
            POST = {'name': 'Test user',
                    'login': 'test@example.com',
                    'password': '12345',
                    'confirm_password': '12345'})
        form = Registration(None, request)
        form.update()
        try:
            form.register_handler()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'http://example.com')

        user = ptah.authService.get_principal_bylogin('test@example.com')
        self.assertIsInstance(user, CrowdUser)
        self.assertEqual(user.name, 'Test user')

        self.assertIn('Validation email has been sent.',
                      request.session['msgservice'][0])
