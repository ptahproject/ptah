import transaction
import ptah
from ptah import config, crowd
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPException, HTTPFound

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
