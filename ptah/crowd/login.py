""" login form """
from memphis import view, form
from pyramid import security
from webob.exc import HTTPFound
from zope.component import getUtility

from ptah.mail import MAIL
from ptah.interfaces import IAuthentication

from interfaces import _
from schemas import LoginSchema

view.registerRoute('ptah-login', '/login.html')
view.registerRoute('ptah-logout', '/logout.html')
view.registerRoute('ptah-login-success', '/login-success.html')
view.registerRoute('ptah-login-suspended', '/login-suspended.html')


class LoginForm(form.Form):
    view.pyramidView(
        route = 'ptah-login', layout='ptah-crowd',
        template=view.template("ptah.crowd:templates/login.pt"))

    id = 'login-form'
    bane = 'login-form'
    title = _('Login')
    fields = form.Fields(LoginSchema)

    @form.button(_(u"Log in"), actype=form.AC_PRIMARY)
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
                    location='%s/login-suspended.html'%request.application_url)

            headers = security.remember(request, user.login)
            raise HTTPFound(
                headers = headers,
                location = '%s/login-success.html'%request.application_url)

        self.message(_('You enter wrong login or password.'), 'error')

    def update(self):
        super(LoginForm, self).update()

        request = self.request
        auth = getUtility(IAuthentication)

        if auth.getCurrentUser() is not None:
            app_url = request.application_url
            raise HTTPFound(location = '%s/login-success.html'%app_url)


class LoginSuccess(view.View):
    """ Login successful information page. """

    view.pyramidView(
        route = 'ptah-login-success', layout='ptah-crowd',
        template = view.template("ptah.crowd:templates/login-success.pt"))

    def update(self):
        auth = getUtility(IAuthentication)

        user = auth.getCurrentUser()
        if user is None:
            raise HTTPFound(
                location = '%s/login.html'%self.request.application_url)
        else:
            self.user = user.name or user.login


class LoginSuspended(view.View):
    """ Suspended account information page. """

    view.pyramidView(
        route = 'ptah-login-suspended', layout='ptah-crowd',
        template = view.template("ptah.crowd:templates/login-suspended.pt"))

    def update(self):
        self.from_name = MAIL.from_name
        self.from_address = MAIL.from_address
        self.full_address = MAIL.full_from_address


@view.pyramidView(route='ptah-logout')
def logout(request):
    """Logout action"""
    uid = security.authenticated_userid(request)

    if uid is not None:
        view.addMessage(request, _('Logout successful!'), 'info')
        headers = security.forget(request)
        raise HTTPFound(
            headers = headers,
            location = request.application_url)
    else:
        raise HTTPFound(location = request.application_url)
