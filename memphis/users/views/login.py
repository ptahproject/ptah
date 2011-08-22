""" login form """
from urllib import quote, unquote
from zope import interface
from zope.component import getUtility
from pyramid import security
from webob.exc import HTTPFound

from memphis import view, form
from memphis.users.interfaces import _, IAuthentication

from schemas import LoginSchema


view.registerLayout(
    'login', view.INavigationRoot, parent='.',
    template = view.template('memphis.users.views:login-layout.pt'))


class LoginForm(form.Form):
    view.pyramidView(
        'login.html', view.INavigationRoot,
        layout = 'login',
        template=view.template("memphis.users.views:login.pt"))

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
            self.message(self.formErrorsMessage, 'error')
            return

        user = getUtility(IAuthentication).authenticate(
            data['login'], data['password'])

        if user is not None:
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


class LoginSuccess(object):
    view.pyramidView(
        'login-success.html', view.INavigationRoot,
        layout = 'login',
        template = view.template("memphis.users.views:login-success.pt"))

    def __init__(self, request):
        self.request = request

    def update(self):
        auth = getUtility(IAuthentication)

        user = auth.getCurrentUser()
        if user is None:
            raise HTTPFound(
                location = '%s/login.html'%self.request.application_url)
        else:
            self.user = user.title or user.login


@view.pyramidView('logout.html', view.INavigationRoot)
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
