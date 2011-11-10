""" add/edit user """
from zope import interface
from ptah import config, view, form
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah.events import PrincipalAddedEvent

from settings import _
from module import CrowdModule
from provider import CrowdUser, Session
from schemas import UserSchema, ManagerChangePasswordSchema
from module import UserWrapper
from ptah.crowd.memberprops import get_properties


class CreateUserForm(form.Form):
    view.pview('create.html', CrowdModule)

    __intr_path__ = '/ptah-manage/crowd/create.html'

    csrf = True
    label = _('Create new user')
    fields = UserSchema

    @form.button(_('Create'), actype=form.AC_PRIMARY)
    def create(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        # create user
        user = CrowdUser(data['name'], data['login'], data['login'])

        # set password
        user.password = ptah.passwordTool.encode(data['password'])
        Session.add(user)
        Session.flush()

        self.request.registry.notify(PrincipalAddedEvent(user))

        props = get_properties(user.uri)
        props.validated = data['validated']
        props.suspended = data['suspended']

        self.message('User has been created.', 'success')
        return HTTPFound(location='.')

    @form.button(_('Back'))
    def back(self):
        raise HTTPFound(location='.')


class ModifyUserForm(form.Form):
    view.pview(context=UserWrapper)

    __intr_path__ = '/ptah-manage/crowd/${user}/'

    csrf = True
    label = 'Update user'
    fields = form.Fieldset(UserSchema)

    def form_content(self):
        user = self.context.user
        props = get_properties(user.uri)

        return {'name': user.name,
                'login': user.login,
                'password': '',
                'validated': props.validated,
                'suspended': props.suspended}

    @form.button(_('Modify'), actype=form.AC_PRIMARY)
    def modify(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        user = self.context.user

        user.name = data['name']
        user.login = data['login']
        user.email = data['login']
        user.password = ptah.passwordTool.encode(data['password'])

        props = get_properties(user.uri)
        props.validated = data['validated']
        props.suspended = data['suspended']

        self.message("User properties has been updated.", 'info')

    @form.button(_('Remove'), actype=form.AC_DANGER)
    def remove(self):
        self.validate_csrf_token()

        user = self.context.user
        Session.delete(user)
        Session.flush()

        self.message("User has been removed.", 'info')
        raise HTTPFound(location='..')

    @form.button(_('Change password'), name='changepwd')
    def password(self):
        raise HTTPFound(location='password.html')

    @form.button(_('Back'))
    def back(self):
        raise HTTPFound(location='..')


class ChangePasswordForm(form.Form):
    view.pview('password.html', UserWrapper)

    __intr_path__ = '/ptah-manage/crowd/${user}/password.html'

    csrf = True
    fields = form.Fieldset(ManagerChangePasswordSchema)

    label = _('Change password')
    description = _('Please specify password for this users.')

    @form.button(_('Change'), actype=form.AC_PRIMARY)
    def change(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        sm = self.request.registry

        self.context.user.password = \
            ptah.passwordTool.encode(data['password'])

        self.message("User password has been changed.")

    @form.button(_('Back'))
    def back(self):
        raise HTTPFound(location='..')
