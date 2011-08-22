""" site registration form """
from zope import event, interface
from zope.component import getUtility
from zope.lifecycleevent import ObjectCreatedEvent

from pyramid import security
from webob.exc import HTTPFound

from memphis import view, form
from memphis.users.interfaces import _, IPasswordTool, IAuthentication

from schemas import RegistrationSchema, PasswordSchema


class Registration(form.Form):
    view.pyramidView('join.html', view.INavigationRoot, layout='login')

    label = _("Registration form")
    fields = form.Fields(RegistrationSchema, PasswordSchema)

    def create(self, data):
        # create user
        item = storage.insertItem('memphis.user')

        datasheet = IUserInfo(item)
        datasheet.login = data['login']
        datasheet.fullname = u'%s %s'%(data['firstname'], data['lastname'])
        datasheet.confirmed = True

        # set password
        passwordtool = getUtility(IPasswordTool)
        datasheet.password = passwordtool.encodePassword(data['password'])

        event.notify(ObjectCreatedEvent(item))
        return item

    @form.button(_(u"Register"), primary=True)
    def handle_register(self):
        request = self.request

        data, errors = self.extractData()
        if errors:
            self.message(errors, 'form-error')
            return

        self.setPrincipal(self.create(data))

        user = getUtility(IAuthentication).getUserByLogin(data['login'])
        headers = security.remember(request, user.id)

        raise HTTPFound(
            location='%s/login-success.html'%request.application_url,
            headers = headers)
