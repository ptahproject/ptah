import transaction
import ptah
from ptah import config, crowd
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPForbidden

from base import Base


class TestCreateUser(Base):

    def test_create_user_back(self):
        from ptah.crowd.module import CrowdModule
        from ptah.crowd.user import CreateUserForm

        request = DummyRequest(
            POST = {'form.buttons.back': 'Back'})
        mod = CrowdModule(None, request)

        view = CreateUserForm(mod, request)
        try:
            view.update()
        except Exception, res:
            pass
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')

    def test_create_user_error(self):
        from ptah.crowd.module import CrowdModule
        from ptah.crowd.user import CreateUserForm

        f = CreateUserForm(None, None)

        request = DummyRequest(
            POST = {'form.buttons.create': 'Create',
                    CreateUserForm.csrfname: f.token})
        mod = CrowdModule(None, request)

        view = CreateUserForm(mod, request)
        view.update()
        self.assertIn(
            'Please fix indicated errors.', 
            request.session['msgservice'][0])

    def test_create_user(self):
        from ptah.crowd.module import CrowdModule
        from ptah.crowd.user import CreateUserForm

        f = CreateUserForm(None, None)

        request = DummyRequest(
            POST = {'name': 'NKim',
                    'login': 'ptah@ptahproject.org',
                    'password': '12345',
                    'validated': 'false',
                    'suspended': 'true',
                    'form.buttons.create': 'Create',
                    CreateUserForm.csrfname: f.token})
        mod = CrowdModule(None, request)

        view = CreateUserForm(mod, request)
        try:
            view.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')
        self.assertIn(
            'User has been created.', 
            request.session['msgservice'][0])

        user = ptah.authService.get_principal_bylogin('ptah@ptahproject.org')
        self.assertEqual(user.name, 'NKim')
        self.assertEqual(user.login, 'ptah@ptahproject.org')

        props = ptah.crowd.query_properties(user.uri)
        self.assertTrue(props.suspended)
        self.assertFalse(props.validated)


class TestModifyUser(Base):

    def _user(self):
        from ptah.crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'ptah@local', 'ptah@local')
        uri = user.uri
        Session.add(user)
        Session.flush()
        return user
        
    def test_modify_user_back(self):
        from ptah.crowd.module import UserWrapper
        from ptah.crowd.user import ModifyUserForm

        user = self._user()
        
        request = DummyRequest(
            POST = {'form.buttons.back': 'Back'})
        wrapper = UserWrapper(user, request)

        view = ModifyUserForm(wrapper, request)
        try:
            view.update()
        except Exception, res:
            pass
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

    def test_modify_user_changepwd(self):
        from ptah.crowd.module import UserWrapper
        from ptah.crowd.user import ModifyUserForm

        user = self._user()
        
        request = DummyRequest(
            POST = {'form.buttons.changepwd': 'Change'})
        wrapper = UserWrapper(user, request)

        view = ModifyUserForm(wrapper, request)
        try:
            view.update()
        except Exception, res:
            pass
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'password.html')

    def test_modify_user_forbidden(self):
        from ptah.crowd.module import UserWrapper
        from ptah.crowd.user import ModifyUserForm

        user = self._user()
        
        request = DummyRequest(
            POST = {'form.buttons.modify': 'Modify',
                    'name': 'NKim',
                    'login': 'ptah@ptahproject.org',
                    'password': '12345',
                    'validated': 'false',
                    'suspended': 'true',
                    })
        wrapper = UserWrapper(user, request)

        view = ModifyUserForm(wrapper, request)
        try:
            view.update()
        except Exception, res:
            pass
        self.assertIsInstance(res, HTTPForbidden)
        self.assertEqual(str(res), 'Form authenticator is not found.')

    def test_modify_user_error(self):
        from ptah.crowd.module import UserWrapper
        from ptah.crowd.user import ModifyUserForm

        user = self._user()
        f = ModifyUserForm(None, None)
        
        request = DummyRequest(
            POST = {'form.buttons.modify': 'Modify',
                    ModifyUserForm.csrfname: f.token})
        wrapper = UserWrapper(user, request)

        view = ModifyUserForm(wrapper, request)
        view.update()

        self.assertIn(
            'Please fix indicated errors.', 
            request.session['msgservice'][0])

    def test_modify_user(self):
        from ptah.crowd.module import UserWrapper
        from ptah.crowd.user import ModifyUserForm

        user = self._user()
        f = ModifyUserForm(None, None)
        
        request = DummyRequest(
            POST = {'form.buttons.modify': 'Modify',
                    'name': 'NKim',
                    'login': 'ptah@ptahproject.org',
                    'password': '12345',
                    'validated': 'false',
                    'suspended': 'true',
                    ModifyUserForm.csrfname: f.token})
        wrapper = UserWrapper(user, request)

        view = ModifyUserForm(wrapper, request)
        view.update()

        self.assertEqual(user.name, 'NKim')
        self.assertEqual(user.login, 'ptah@ptahproject.org')

    def test_modify_user_remove(self):
        from ptah.crowd.module import UserWrapper
        from ptah.crowd.user import ModifyUserForm
        from ptah.crowd.provider import CrowdUser

        user = self._user()
        f = ModifyUserForm(None, None)
        
        request = DummyRequest(
            POST = {'form.buttons.remove': 'Remove',
                    ModifyUserForm.csrfname: f.token})
        wrapper = UserWrapper(user, request)

        view = ModifyUserForm(wrapper, request)
        try:
            view.update()
        except Exception, res:
            pass
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

        user = CrowdUser.get_byuri(user.uri)
        self.assertIsNone(user)


class TestChangePassword(Base):

    def _user(self):
        from ptah.crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'ptah@local', 'ptah@local')
        uri = user.uri
        Session.add(user)
        Session.flush()
        return user
        
    def test_change_password_user_back(self):
        from ptah.crowd.module import UserWrapper
        from ptah.crowd.user import ChangePasswordForm

        user = self._user()
        
        request = DummyRequest(
            POST = {'form.buttons.back': 'Back'})
        wrapper = UserWrapper(user, request)

        view = ChangePasswordForm(wrapper, request)
        try:
            view.update()
        except Exception, res:
            pass
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

    def test_change_password_forbidden(self):
        from ptah.crowd.module import UserWrapper
        from ptah.crowd.user import ChangePasswordForm

        user = self._user()
        
        request = DummyRequest(
            POST = {'form.buttons.change': 'Change',
                    'password': '12345',
                    })
        wrapper = UserWrapper(user, request)

        view = ChangePasswordForm(wrapper, request)
        try:
            view.update()
        except Exception, res:
            pass
        self.assertIsInstance(res, HTTPForbidden)
        self.assertEqual(str(res), 'Form authenticator is not found.')

    def test_change_password_error(self):
        from ptah.crowd.module import UserWrapper
        from ptah.crowd.user import ChangePasswordForm

        user = self._user()
        f = ChangePasswordForm(None, None)
        
        request = DummyRequest(
            POST = {'form.buttons.change': 'Change',
                    ChangePasswordForm.csrfname: f.token})
        wrapper = UserWrapper(user, request)

        view = ChangePasswordForm(wrapper, request)
        view.update()

        self.assertIn(
            'Please fix indicated errors.', 
            request.session['msgservice'][0])

    def test_change_password(self):
        from ptah.crowd.module import UserWrapper
        from ptah.crowd.user import ChangePasswordForm

        user = self._user()
        f = ChangePasswordForm(None, None)
        
        request = DummyRequest(
            POST = {'form.buttons.change': 'Change',
                    'password': '12345',
                    ChangePasswordForm.csrfname: f.token})
        wrapper = UserWrapper(user, request)

        view = ChangePasswordForm(wrapper, request)
        view.update()

        self.assertEqual(user.password, '{plain}12345')

