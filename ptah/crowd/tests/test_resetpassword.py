import transaction
import ptah, ptah.crowd
from ptah import config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from base import Base


class TestResetPassword(Base):

    def test_resetpassword_cancel(self):
        from ptah.crowd.resetpassword import ResetPassword
        request = DummyRequest(
            POST={'form.buttons.cancel': 'Cancel'})

        form = ResetPassword(None, request)
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(
            res.headers['location'], 'http://example.com')

    def test_resetpassword_required(self):
        from ptah.crowd.resetpassword import ResetPassword
        request = DummyRequest(
            POST={'form.buttons.reset': 'Reset'})

        form = ResetPassword(None, request)
        form.update()

        msg = request.session['msgservice'][0]
        self.assertIn("System can't restore password for this user.", msg)

    def test_resetpassword(self):
        from ptah.crowd.provider import CrowdUser, Session
        from ptah.crowd.resetpassword import ResetPassword
        from ptah.crowd.resetpassword import ResetPasswordTemplate

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        data = [1, None]
        def send(self):
            data[0] = 2
            data[1] = self.passcode

        ResetPasswordTemplate.send = send

        request = DummyRequest(
            POST={'login': 'login',
                  'form.buttons.reset': 'Reset'})

        form = ResetPassword(None, request)
        try:
            form.update()
        except HTTPFound, res:
            pass

        msg = request.session['msgservice'][0]
        self.assertIn("Password reseting process has been initiated.", msg)

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(
            res.headers['location'], 'http://example.com')
        self.assertEqual(data[0], 2)

        principal = ptah.passwordTool.get_principal(data[1])
        self.assertEqual(principal.name, 'name')
        self.assertEqual(principal.login, 'login')

        del ResetPasswordTemplate.send

    def test_resetpassword_form_unknown_passcode(self):
        from ptah.crowd.resetpassword import ResetPasswordForm

        request = DummyRequest(subpath=('unknown',))

        form = ResetPasswordForm(None, request)
        try:
            form.update()
        except HTTPFound, res:
            pass

        msg = request.session['msgservice'][0]
        self.assertIn("Passcode is invalid.", msg)
        self.assertEqual(
            res.headers['location'], 'http://example.com/resetpassword.html')

    def test_resetpassword_form_update(self):
        from ptah.crowd.provider import CrowdUser, Session
        from ptah.crowd.resetpassword import ResetPasswordForm

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        passcode = ptah.passwordTool.generate_passcode(user)

        request = DummyRequest(subpath=(passcode,))

        form = ResetPasswordForm(None, request)
        form.update()

        self.assertEqual(form.title, user.name)
        self.assertEqual(form.passcode, passcode)

    def test_resetpassword_form_change_errors(self):
        from ptah.crowd.provider import CrowdUser, Session
        from ptah.crowd.resetpassword import ResetPasswordForm

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        passcode = ptah.passwordTool.generate_passcode(user)

        request = DummyRequest(
            subpath=(passcode,),
            POST = {'password': '12345', 'confirm_password': '123456',
                    'form.buttons.change': 'Change'})

        form = ResetPasswordForm(None, request)
        form.update()

        msg = request.session['msgservice'][0]
        self.assertIn("Please fix indicated errors.", msg)

    def test_resetpassword_form_change(self):
        from ptah.crowd.provider import CrowdUser, Session
        from ptah.crowd.resetpassword import ResetPasswordForm

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        passcode = ptah.passwordTool.generate_passcode(user)

        request = DummyRequest(
            subpath=(passcode,),
            POST = {'password': '123456', 'confirm_password': '123456',
                    'form.buttons.change': 'Change'})

        form = ResetPasswordForm(None, request)
        try:
            form.update()
        except HTTPFound, res:
            pass

        msg = request.session['msgservice'][0]
        self.assertIn("You have successfully changed your password.", msg)
        self.assertEqual(res.headers['location'], 'http://example.com')
        self.assertTrue(ptah.passwordTool.check(user.password, '123456'))

    def test_resetpassword_template(self):
        from ptah.crowd.provider import CrowdUser, Session
        from ptah.crowd.resetpassword import ResetPasswordTemplate

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        request = DummyRequest()
        passcode = ptah.passwordTool.generate_passcode(user)

        template = ResetPasswordTemplate(user, request)
        template.passcode = passcode

        template.update()
        text = template.render()

        self.assertIn(
            "Password reseting process has been initiated. You must visit link below to complete password reseting:", text)

        self.assertIn(
            "http://example.com/resetpassword.html/%s/"%passcode, text)
