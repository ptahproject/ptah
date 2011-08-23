""" reset password form """
from datetime import datetime
from pyramid import security
from webob.exc import HTTPFound
from memphis import config, form, view, mail
from ptah.interfaces import IAuthentication

from interfaces import _, IPasswordTool
from schemas import ResetPasswordSchema, PasswordSchema

MAIL = mail.MAIL

view.registerRoute(
    'ptah-resetpassword', '/resetpassword.html', view.DefaultRoot)
view.registerRoute(
    'ptah-resetpassword-form', '/resetpasswordform.html', view.DefaultRoot)


class ResetPassword(form.Form):
    view.pyramidView(
        route = 'ptah-resetpassword', layout='ptah-crowd',
        template = view.template('ptah.crowd:templates/resetpassword.pt'))

    fields = form.Fields(ResetPasswordSchema)

    def getContent(self):
        return {'login': self.request.params.get('login', '')}

    def update(self):
        super(ResetPassword, self).update()

        self.from_name = MAIL.from_name
        self.from_address = MAIL.from_address

    @form.button(_('Start password reset'), primary=True)
    def reset(self):
        request = self.request
        registry = request.registry
        data, errors = self.extractData()

        login = data.get('login')
        if login:
            principal = registry.getUtility(IAuthentication)\
                .getUserByLogin(login)

            if principal is not None:
                passcode = registry.getUtility(IPasswordTool)\
                    .generatePasscode(principal)

                template = ResetPasswordTemplate(principal, request)
                template.passcode = passcode
                template.send()

                self.message(_('Your password has been '
                               'reset and is being emailed to you.'))
                raise HTTPFound(location=request.application_url)

        self.message(_(u"System can't restore password for this user."))

    @form.button(_('Cancel'))
    def cancel(self):
        raise HTTPFound(location=self.request.application_url)
        

class ResetPasswordForm(form.Form):
    view.pyramidView(
        route = 'ptah-resetpassword-form', layout='ptah-crowd',
        template = view.template('ptah.crowd:templates/resetpasswordform.pt'))

    fields = form.Fields(PasswordSchema)
    fields['password'].widgetFactory = form.widgets.PasswordWidget
    fields['confirm_password'].widgetFactory = form.widgets.PasswordWidget

    def update(self):
        request = self.request
        ptool = self.ptool = request.registry.getUtility(IPasswordTool)

        passcode = request.params.get('passcode')
        self.principal = principal = self.ptool.getPrincipal(passcode)

        if principal is not None:
            self.passcode = passcode
            self.title = principal.name or principal.login
        else:
            self.message(_("Passcode is invalid."), 'warning')
            raise HTTPFound(
                location='%s/ptah/resetpassword.html'%request.application_url)

        super(ResetPasswordForm, self).update()

    @form.button(_("Change password and login"), primary=True)
    def changePassword(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
        else:
            try:
                self.ptool.resetPassword(self.passcode, data['password'])
            except Exception, exc:
                self.message(exc, 'error')
                return

            headers = security.remember(self.request, self.principal.login)
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

        self.url = '%s/ptah/resetpasswordform.html?passcode=%s'%(
            request.application_url, self.passcode)

        info = self.context

        self.to_address = mail.formataddr((info.name, info.login))
