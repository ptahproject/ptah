""" site registration form """
from zope import event, interface
from zope.component import getUtility
#from zope.lifecycleevent import ObjectCreatedEvent

from memphis import view, form
from pyramid import security
from webob.exc import HTTPFound

from ptah import models
from ptah.interfaces import _, IPasswordTool, IAuthentication

from schemas import RegistrationSchema, PasswordSchema


class Registration(form.Form):
    view.pyramidView('join.html', view.INavigationRoot, layout='login')

    label = _("Registration form")
    fields = form.Fields(RegistrationSchema, PasswordSchema)

    def create(self, data):
        # create user
        user = models.User(data['fullname'], data['login'], data['login'])

        # set password
        passwordtool = getUtility(IPasswordTool)
        user.password = passwordtool.encodePassword(data['password'])
        models.Session.add(user)
        models.Session.flush()

        #event.notify(ObjectCreatedEvent(item))
        return user

    @form.button(_(u"Register"), primary=True)
    def handleRegister(self):
        data, errors = self.extractData()
        if errors:
            self.message(errors, 'form-error')
            return

        user = self.create(data)

        user = getUtility(IAuthentication).getUserByLogin(data['login'])
        headers = security.remember(self.request, user.id)

        raise HTTPFound(
            location='%s/login-success.html'%self.request.application_url,
            headers = headers)
