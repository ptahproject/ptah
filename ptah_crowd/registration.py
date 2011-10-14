""" user registration form """
from memphis import config, view, form
from pyramid import security
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

import ptah
from ptah.password import PasswordSchema
from ptah.events import PrincipalRegisteredEvent

from settings import _, CROWD
from schemas import RegistrationSchema
from provider import Session, CrowdUser
from validation import initiate_email_validation


view.register_route('ptah-join', '/join.html')


class Registration(form.Form):
    view.pyramidview(route = 'ptah-join', layout='ptah-page')

    label = _("Registration")
    fields = form.Fieldset(RegistrationSchema, PasswordSchema)
    autocomplete = 'off'

    def update(self):
        uri = ptah.authService.get_userid()
        if uri is not None:
            raise HTTPFound(location = self.request.application_url)

        if not CROWD.join:
            raise HTTPForbidden('Site registraion is disabled.')

        super(Registration, self).update()

    def create(self, data):
        # create user
        user = CrowdUser(data['name'], data['login'], data['login'])

        # set password
        user.password = ptah.passwordTool.encodePassword(data['password'])
        Session.add(user)
        Session.flush()

        return user

    @form.button(_(u"Register"), actype=form.AC_PRIMARY)
    def register_handler(self):
        data, errors = self.extract()
        if errors:
            self.message(errors, 'form-error')
            return

        user = self.create(data)
        config.notify(PrincipalRegisteredEvent(user))

        # validation
        if CROWD.validation:
            initiate_email_validation(user.email, user, self.request)
            self.message('Validation email has been sent.')
            if not CROWD['allow-unvalidated']:
                raise HTTPFound(location=self.request.application_url)

        # authenticate
        info = ptah.authService.authenticate(
            {'login': user.login, 'password': user.password})
        if info.status:
            headers = security.remember(self.request, user.uri)
            raise HTTPFound(
                location='%s/login-success.html'%self.request.application_url,
                headers = headers)
        else:
            self.message(info.message) # pragma: no cover
