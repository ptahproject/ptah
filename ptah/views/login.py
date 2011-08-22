""" login form """
from memphis import view, form
from pyramid import security
from webob.exc import HTTPFound
from zope.component import getUtility

from memphis.mail import MAIL

from ptah.interfaces import _, IAuthentication, IPtahRoute
from ptah.layout import ptahRoute
from ptah.views.schemas import LoginSchema


view.registerRoute('ptah-login', '/login.html',
                   lambda request: ptahRoute)

view.registerRoute('ptah-logout', '/logout.html',
                   lambda request: ptahRoute)


class LoginForm(form.Form):
    view.pyramidView(
        route = 'ptah-login',
        template=view.template("ptah.views:login.pt"))

    id = 'login-form'
    bane = 'login-form'
    title = _('Login')
    fields = form.Fields(LoginSchema)
    fields['password'].widgetFactory = form.widgets.PasswordWidget

    @form.button(_(u"Log in"), primary=True)
    def handleLogin(self):
        request = self.request

        data, errors = self.extractData()
        if errors:
            self.message(errors, 'form-error')
            return

        user = getUtility(IAuthentication).authenticate(
            data['login'], data['password'])

        if user is not None:
            if user.suspended:
                raise HTTPFound(
                    location='%s/ptah/suspended.html'%request.application_url)
                
            headers = security.remember(request, user.login)
            raise HTTPFound(
                headers = headers,
                location = '%s/ptah/success.html'%request.application_url)

        self.message(_('You enter wrong login or password.'), 'error')

    def update(self):
        super(LoginForm, self).update()

        request = self.request
        auth = getUtility(IAuthentication)

        if auth.getCurrentUser() is not None:
            app_url = request.application_url
            raise HTTPFound(location = '%s/ptah/success.html'%app_url)


class LoginSuccess(view.View):
    view.pyramidView(
        'success.html', IPtahRoute, route = 'ptah',
        template = view.template("ptah.views:login-success.pt"))

    def update(self):
        auth = getUtility(IAuthentication)

        user = auth.getCurrentUser()
        if user is None:
            raise HTTPFound(
                location = '%s/login.html'%self.request.application_url)
        else:
            self.user = user.name or user.login


class LoginSuspended(view.View):
    view.pyramidView(
        'suspended.html', IPtahRoute, route = 'ptah',
        template = view.template("ptah.views:login-suspended.pt"))

    def update(self):
        self.from_name = MAIL.from_name
        self.from_address = MAIL.from_address
        self.full_address = MAIL.full_from_address


@view.pyramidView(route='ptah-logout')
def logout(request):
    uid = security.authenticated_userid(request)

    if uid is not None:
        view.addMessage(request, _('Logout successful!'), 'info')
        headers = security.forget(request)
        raise HTTPFound(
            headers = headers,
            location = request.application_url)
    else:
        raise HTTPFound(location = request.application_url)
