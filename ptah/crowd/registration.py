""" site registration form """
from zope import interface
#from zope.lifecycleevent import ObjectCreatedEvent

from memphis import view, form
from pyramid import security
from webob.exc import HTTPFound, HTTPForbidden
from ptah.interfaces import IAuthentication

import validation
from interfaces import _, IPasswordTool
from settings import CROWD
from models import Session, CrowdUser
from schemas import RegistrationSchema, PasswordSchema


view.registerRoute('ptah-join', '/join.html')


class Registration(form.Form):
    view.pyramidView(route = 'ptah-join', layout='ptah-crowd')

    csrf = True
    label = _("Registration")
    fields = form.Fields(RegistrationSchema, PasswordSchema)

    def update(self):
        if not CROWD.registration:
            raise HTTPForbidden('Site registraion is disabled.')

        super(Registration, self).update()

    def create(self, data):
        # create user
        user = CrowdUser(data['fullname'], data['login'], data['login'])

        # set password
        passwordtool = self.request.registry.getUtility(IPasswordTool)
        user.password = passwordtool.encodePassword(data['password'])
        Session.add(user)
        Session.flush()

        #config.notify(ObjectCreatedEvent(item))
        return user

    @form.button(_(u"Register"), actype=form.AC_PRIMARY)
    def handleRegister(self):
        data, errors = self.extractData()
        if errors:
            self.message(errors, 'form-error')
            return

        reg = self.request.registry

        user = self.create(data)

        user = reg.getUtility(IAuthentication).getUserByLogin(data['login'])
        headers = security.remember(self.request, user.login)

        validation.initiateValidation(user, self.request)

        raise HTTPFound(
            location='%s/login-success.html'%self.request.application_url,
            headers = headers)
