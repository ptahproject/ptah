""" login form """
from memphis import view, form
from pyramid import security
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import authService
from ptah.mail import MAIL
from ptah.crowd import _

view.registerRoute('ptah-login', '/login.html')
view.registerRoute('ptah-logout', '/logout.html')
view.registerRoute('ptah-login-success', '/login-success.html')
view.registerRoute('ptah-login-suspended', '/login-suspended.html')


class LoginForm(form.Form):
    view.pyramidView(
        route='ptah-login', layout='ptah-security',
        template = view.template("ptah.crowd:templates/login.pt"))

    id = 'login-form'
    title = _('Login')

    fields = form.Fieldset(
        form.fields.TextField(
            'login',
            title = _(u'Login Name'),
            description = _('Login names are case sensitive, '\
                                'make sure the caps lock key is not enabled.'),
            default = u''),

        form.fields.PasswordField(
            'password',
            title = _(u'Password'),
            description = _('Case sensitive, make sure caps '\
                                'lock is not enabled.'),
            default = u''),
        )

    @form.button(_(u"Log in"), actype=form.AC_PRIMARY)
    def handleLogin(self):
        request = self.request

        data, errors = self.extract()
        if errors:
            self.message(errors, 'form-error')
            return

        info = authService.authenticate(data)

        if info.status:
            request.registry.notify(
                ptah.events.LoggedInEvent(info.principal))

            headers = security.remember(request, info.principal.uri)
            raise HTTPFound(
                headers = headers,
                location = '%s/login-success.html'%request.application_url)

        if info.principal is not None:
            request.registry.notify(
                ptah.events.LoginFailedEvent(info.principal, info.message))

        if info.arguments.get('suspended'):
            raise HTTPFound(
                location='%s/login-suspended.html'%request.application_url)

        if info.message:
            self.message(info.message, 'warning')
            return

        self.message(_('You enter wrong login or password.'), 'error')

    def update(self):
        self.registration = ptah.PTAH_CONFIG.registration

        if authService.getUserId():
            app_url = self.request.application_url
            raise HTTPFound(location = '%s/login-success.html'%app_url)

        super(LoginForm, self).update()


class LoginSuccess(view.View):
    """ Login successful information page. """

    view.pyramidView(
        route = 'ptah-login-success', layout='ptah-security',
        template = view.template("ptah.crowd:templates/login-success.pt"))

    def update(self):
        user = authService.getCurrentPrincipal()
        if user is None:
            headers = []
            request = self.request
            uid = security.authenticated_userid(request)
            if uid:
                headers = security.forget(request)

            raise HTTPFound(
                headers = headers,
                location = '%s/login.html'%request.application_url)
        else:
            self.user = user.name or user.login


class LoginSuspended(view.View):
    """ Suspended account information page. """

    view.pyramidView(
        route = 'ptah-login-suspended', layout='ptah-security',
        template = view.template("ptah.crowd:templates/login-suspended.pt"))

    def update(self):
        self.from_name = MAIL.from_name
        self.from_address = MAIL.from_address
        self.full_address = MAIL.full_from_address


@view.pyramidView(route='ptah-logout')
def logout(request):
    """Logout action"""
    authService.setUserId(None)
    uid = security.authenticated_userid(request)

    if uid is not None:
        request.registry.notify(
            ptah.events.LoggedOutEvent(ptah.resolve(uid)))

        view.addMessage(request, _('Logout successful!'), 'info')
        headers = security.forget(request)
        raise HTTPFound(
            headers = headers,
            location = request.application_url)
    else:
        raise HTTPFound(location = request.application_url)
