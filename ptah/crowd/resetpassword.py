""" reset password form """
from datetime import datetime
from ptah import config, form, view
from pyramid import security
from pyramid.httpexceptions import HTTPFound

from ptah import mail
from ptah import authService
from ptah import passwordTool
from ptah.password import PasswordSchema
from ptah.events import ResetPasswordInitiatedEvent
from ptah.events import PrincipalPasswordChangedEvent

from settings import _

view.register_route('ptah-resetpassword', '/resetpassword.html')
view.register_route('ptah-resetpassword-form', '/resetpassword.html/*subpath')


class ResetPassword(form.Form):
    view.pview(
        route = 'ptah-resetpassword', layout='ptah-page',
        template = view.template('ptah.crowd:templates/resetpassword.pt'))

    fields = form.Fieldset(
        form.FieldFactory(
            'text',
            'login',
            title = _(u'Login Name'),
            description = _('Login names are not case sensitive.'),
            missing = u'',
            default = u''))

    def form_content(self):
        return {'login': self.request.params.get('login', '')}

    def update(self):
        self.from_name = mail.MAIL.from_name
        self.from_address = mail.MAIL.from_address

        super(ResetPassword, self).update()

    @form.button(_('Start password reset'),name='reset',actype=form.AC_PRIMARY)
    def reset(self):
        request = self.request
        registry = request.registry
        data, errors = self.extract()

        login = data.get('login')
        if login:
            principal = authService.get_principal_bylogin(login)

            if principal is not None and \
                   passwordTool.can_change_password(principal):

                passcode = passwordTool.generate_passcode(principal)

                template = ResetPasswordTemplate(
                    principal, request, passcode = passcode)
                template.send()

                self.request.registry.notify(
                    ResetPasswordInitiatedEvent(principal))

                self.message(_('Password reseting process has been initiated. '
                               'Check your email for futher instructions.'))
                raise HTTPFound(location=request.application_url)

        self.message(_(u"System can't restore password for this user."))

    @form.button(_('Cancel'))
    def cancel(self):
        raise HTTPFound(location=self.request.application_url)


class ResetPasswordForm(form.Form):
    view.pview(
        route = 'ptah-resetpassword-form', layout='ptah-page',
        template=view.template('ptah.crowd:templates/resetpasswordform.pt'))

    fields = PasswordSchema

    def update(self):
        request = self.request

        passcode = request.subpath[0]
        self.principal = principal = passwordTool.get_principal(passcode)

        if principal is not None and \
               passwordTool.can_change_password(principal):
            self.passcode = passcode
            self.title = principal.name or principal.login
        else:
            self.message(_("Passcode is invalid."), 'warning')
            raise HTTPFound(
                location='%s/resetpassword.html'%request.application_url)

        super(ResetPasswordForm, self).update()

    @form.button(_("Change password"), name='change', actype=form.AC_PRIMARY)
    def changePassword(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
        else:
            principal = passwordTool.get_principal(self.passcode)
            passwordTool.change_password(self.passcode, data['password'])

            self.request.registry.notify(
                PrincipalPasswordChangedEvent(principal))

            # check if principal can be authenticated
            info = authService.authenticate_principal(principal)

            headers = []
            if info.status:
                headers = security.remember(self.request, self.principal.uri)

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

        self.url = '%s/resetpassword.html/%s/'%(
            request.application_url, self.passcode)

        info = self.context

        self.to_address = mail.formataddr((info.name, info.login))
