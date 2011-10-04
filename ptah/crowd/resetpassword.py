""" reset password form """
import colander
from datetime import datetime
from memphis import config, form, view
from pyramid import security
from pyramid.httpexceptions import HTTPFound

from ptah import mail
from ptah import authService
from ptah import passwordTool
from ptah.password import PasswordSchema
from ptah.events import ResetPasswordInitiatedEvent
from ptah.events import PrincipalPasswordChangedEvent

from ptah.crowd import _

view.registerRoute('ptah-resetpassword', '/resetpassword.html')
view.registerRoute('ptah-resetpassword-form', '/resetpasswordform.html')


class ResetPasswordSchema(colander.Schema):
    """ reset password """

    login = colander.SchemaNode(
        colander.Str(),
        title = _(u'Login Name'),
        description = _('Login names are not case sensitive.'),
        missing = u'',
        default = u'')


class ResetPassword(form.Form):
    view.pyramidView(
        route = 'ptah-resetpassword', layout='ptah-security',
        template = view.template('ptah.crowd:templates/resetpassword.pt'))

    csrf = True
    fields = form.Fieldset(ResetPasswordSchema)

    def getContent(self):
        return {'login': self.request.params.get('login', '')}

    def update(self):
        super(ResetPassword, self).update()

        self.from_name = mail.MAIL.from_name
        self.from_address = mail.MAIL.from_address

    @form.button(_('Start password reset'), actype=form.AC_PRIMARY)
    def reset(self):
        request = self.request
        registry = request.registry
        data, errors = self.extractData()

        login = data.get('login')
        if login:
            principal = authService.getPrincipalByLogin(login)

            if principal is not None and \
                   passwordTool.hasPasswordChanger(principal.uri):

                passcode = passwordTool.generatePasscode(principal.uri)

                template = ResetPasswordTemplate(principal, request)
                template.passcode = passcode
                template.send()

                self.request.registry.notify(
                    ResetPasswordInitiatedEvent(principal))

                self.message(_('Your password has been '
                               'reset and is being emailed to you.'))
                raise HTTPFound(location=request.application_url)

        self.message(_(u"System can't restore password for this user."))

    @form.button(_('Cancel'))
    def cancel(self):
        raise HTTPFound(location=self.request.application_url)


class ResetPasswordForm(form.Form):
    view.pyramidView(
        route = 'ptah-resetpassword-form', layout='ptah-security',
        template=view.template('ptah.crowd:templates/resetpasswordform.pt'))

    csrf = True
    fields = form.Fieldset(PasswordSchema)

    def update(self):
        request = self.request
        passcode = request.params.get('passcode')
        self.principal = principal = passwordTool.getPrincipal(passcode)

        if principal is not None and \
               passwordTool.hasPasswordChanger(principal.uri):
            self.passcode = passcode
            self.title = principal.name or principal.login
        else:
            self.message(_("Passcode is invalid."), 'warning')
            raise HTTPFound(
                location='%s/resetpassword.html'%request.application_url)

        super(ResetPasswordForm, self).update()

    @form.button(_("Change password and login"), actype=form.AC_PRIMARY)
    def changePassword(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
        else:
            principal = passwordTool.getPrincipal(self.passcode)
            passwordTool.changePassword(self.passcode, data['password'])

            self.request.registry.notify(
                PrincipalPasswordChangedEvent(principal))

            # check if principal can be authenticated
            info = authService.authenticatePrincipal(principal)

            if info.status:
                headers = security.remember(self.request, self.principal.uri)
            else:
                headers = []

            self.message(
                _('You have successfully changed your password.'), 'success')
            raise HTTPFound(
                headers = headers,
                location = self.request.application_url)


class ResetPasswordTemplate(mail.MailTemplate):

    subject = 'Password Reset Confirmation'
    template = view.template('ptah.crowd:templates/resetpasswordmail.pt')

    def update(self):
        super(ResetPasswordTemplate, self).update()

        request = self.request

        self.date = datetime.now()

        remoteAddr = request.get('REMOTE_ADDR', '')
        forwardedFor = request.get('HTTP_X_FORWARDED_FOR', None)

        self.from_ip = (forwardedFor and '%s/%s' %
                        (remoteAddr, forwardedFor) or remoteAddr)

        self.url = '%s/resetpasswordform.html?passcode=%s'%(
            request.application_url, self.passcode)

        info = self.context

        self.to_address = mail.formataddr((info.name, info.login))
