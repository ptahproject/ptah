""" site registration form """
from zope import interface
from memphis import view, form
from pyramid import security
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

import ptah
from ptah import authService
from ptah.password import PasswordSchema
from ptah.events import PrincipalRegisteredEvent

from ptah.crowd import _
from schemas import RegistrationSchema
from provider import Session, CrowdUser


view.registerRoute('ptah-join', '/join.html')


class Registration(form.Form):
    view.pyramidView(route = 'ptah-join', layout='ptah-security')

    csrf = True
    label = _("Registration")
    fields = form.Fieldset(RegistrationSchema, PasswordSchema)
    autocomplete = 'off'

    def update(self):
        if not ptah.PTAH_CONFIG.registration:
            raise HTTPForbidden('Site registraion is disabled.')

        sm = self.request.registry

        fieldsets = []
        self.props = props = []
        #for name, prop in sm.getUtilitiesFor(IPreferencesGroup):
        #    props.append(prop)
        #    fieldsets.append(form.Fieldset(prop.schema))

        self.fields = form.Fieldset(RegistrationSchema,PasswordSchema,*fieldsets)

        super(Registration, self).update()

    def create(self, data):
        # create user
        user = CrowdUser(data['name'], data['login'], data['login'])

        # set password
        user.password = ptah.passwordtool.encodePassword(data['password'])
        Session.add(user)
        Session.flush()

        for prop in self.props:
            propdata = data.get(prop.name)
            prop.create(user.id, **propdata)

        return user

    @form.button(_(u"Register"), actype=form.AC_PRIMARY)
    def handleRegister(self):
        data, errors = self.extractData()
        if errors:
            self.message(errors, 'form-error')
            return

        user = self.create(data)

        sm = self.request.registry
        sm.notify(PrincipalRegisteredEvent(user))

        principal = authService.authenticate(
            {'login': data['name'], 'password': data['password']})
        if principal is not None:
            headers = security.remember(self.request, user.uri)
            raise HTTPFound(
                location='%s/login-success.html'%self.request.application_url,
                headers = headers)
        else:
            raise HTTPFound(location=self.request.application_url)
