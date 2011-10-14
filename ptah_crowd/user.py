""" add/edit user """
from zope import interface
from memphis import config, view, form
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah.events import PrincipalAddedEvent

from settings import _
from module import CrowdModule
from provider import CrowdUser, Session
from schemas import UserSchema, ManagerChangePasswordSchema
from module import UserWrapper


class CreateUserForm(form.Form):
    view.pyramidview('create.html', CrowdModule)

    __intr_path__ = '/ptah-manage/crowd/create.html'

    csrf = True
    label = _('Create new user')
    fields = UserSchema.omit('id', 'joined')

    @form.button(_('Create'), actype=form.AC_PRIMARY)
    def create(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        # create user
        user = CrowdUser(data['name'], data['login'], data['login'])
        # set password
        user.password = ptah.passwordTool.encodePassword(data['password'])
        Session.add(user)
        Session.flush()

        self.request.registry.notify(PrincipalAddedEvent(user))

        self.message('User has been created.', 'success')
        raise HTTPFound(location='./')


class UserInfo(form.Form):
    view.pyramidview(context=UserWrapper)

    __intr_path__ = '/ptah-manage/crowd/${user}/'

    csrf = True
    label = 'Update user'
    fields = form.Fieldset(UserSchema).omit('id')

    def form_content(self):
        user = self.context.user
        return {'name': user.name,
                'login': user.login,
                'password': ''}

    @form.button(_('Modify'), actype=form.AC_PRIMARY)
    def modify(self):
        #user.validated = True
        #self.message("Account  has been validated.", 'info')
        pass

    @form.button(_('Remove'), actype=form.AC_DANGER)
    def remove(self):
        #user.validated = True
        #self.message("Account  has been validated.", 'info')
        pass

    @form.button(_('Back'))
    def back(self):
        raise HTTPFound(location='..')


class ChangePassword(form.Form):
    view.pyramidview('password.html', UserWrapper)

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
            ptah.passwordTool.encodePassword(data['password'])

        self.message("User password has been changed.")
