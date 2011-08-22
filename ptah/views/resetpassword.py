""" reset password form """
from datetime import datetime
from pyramid import security
from webob.exc import HTTPFound

from zope import interface, schema
from zope.component import getUtility

from memphis import config, form, view, mail
from ptah.interfaces import _, IPasswordTool, IAuthentication

from schemas import ResetPasswordSchema, PasswordSchema

MAIL = mail.MAIL


class ResetPassword(view.View):
    view.pyramidView(
        'resetpassword.html', view.INavigationRoot,
        layout = 'login',
        template = view.template('ptah.views:resetpassword.pt'))

    fields = form.Fields(ResetPasswordSchema)

    def update(self):
        super(ResetPassword, self).update()

        self.from_name = MAIL.from_name
        self.from_address = MAIL.from_address

        request = self.request

        if request.params.has_key('button.send'):
            login = request.params.get('login', '')

            principal = getUtility(IAuthentication).getUserByLogin(login)
            if principal is not None:
                passcode = getUtility(
                    IPasswordTool).generatePasscode(principal)

                template = ResetPasswordTemplate(principal, request)
                template.passcode = passcode
                template.send()

                self.message(_('Your password has been '
                               'reset and is being emailed to you.'))
                raise HTTPFound(location=request.application_url)

            self.message(_(u"System can't restore password for this user."))


class ResetPasswordForm(form.Form):
    view.pyramidView(
        'resetpasswordform.html', view.INavigationRoot,
        layout = 'login',
        template = view.template('ptah.views:resetpasswordform.pt'))

    fields = form.Fields(PasswordSchema)
    fields['password'].widgetFactory = form.widgets.PasswordWidget
    fields['confirm_password'].widgetFactory = form.widgets.PasswordWidget

    def update(self):
        request = self.request
        ptool = self.ptool = getUtility(IPasswordTool)

        passcode = request.params.get('passcode')
        self.principal = principal = self.ptool.getPrincipal(passcode)

        if principal is not None:
            self.passcode = passcode
            self.title = principal.name or principal.login
        else:
            self.message(_("Passcode is invalid."), 'warning')
            raise HTTPFound(
                location='%s/resetpassword.html'%request.application_url)

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
    template = view.template('ptah.views:resetpasswordmail.pt')

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
