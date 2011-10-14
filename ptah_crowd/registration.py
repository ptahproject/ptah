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
from validation import initiate_validation


view.registerRoute('ptah-join', '/join.html')


class Registration(form.Form):
    view.pyramidView(route = 'ptah-join', layout='ptah-security')

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
    def handleRegister(self):
        data, errors = self.extract()
        if errors:
            self.message(errors, 'form-error')
            return

        user = self.create(data)
        config.notify(PrincipalRegisteredEvent(user))

        # validation
        if CROWD.validation:
            initiate_validation(user, self.request)
            self.message('Validation email has been sent.')

        # authenticate
        principal = ptah.authService.authenticate(
            {'login': data['name'], 'password': data['password']})
        if principal is not None:
            headers = security.remember(self.request, user.uri)
            raise HTTPFound(
                location='%s/login-success.html'%self.request.application_url,
                headers = headers)
        else:
            raise HTTPFound(location=self.request.application_url)
