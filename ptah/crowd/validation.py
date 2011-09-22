""" account validation/suspending """
from datetime import timedelta, datetime
from memphis import view, config
from pyramid.security import remember
from pyramid.httpexceptions import HTTPFound
from pyramid.threadlocal import get_current_request

import ptah
from ptah import token, mail

from memberprops import MemberProperties
from interfaces import IPrincipalWithEmail

TOKEN_TYPE = token.registerTokenType(
    '5cfcb3e2-e93f-42f7-9d1c-59077952bd72', timedelta(hours=24))


@ptah.registerAuthChecker
def validationAndSuspendedChecker(principal, info):
    props = MemberProperties.get(principal.uuid)
    if props.suspended:
        info.message = 'Account is suspended.'
        info.keywords['suspended'] = True
        return False

    if not ptah.PTAH_CONFIG['validation']:
        return True

    if ptah.PTAH_CONFIG['allow-unvalidated'] or props.validated:
        return True

    info.message = 'Account is not validated.'
    info.keywords['validation'] = False
    return False


def initiateValidation(principal, request):
    view.addMessage(request, 'Validation email has been sent.')
    t = token.tokenService.generate(TOKEN_TYPE, principal.uuid)
    template = ValidationTemplate(principal, request)
    template.token = t
    template.send()


@config.handler(ptah.events.PrincipalRegisteredEvent)
def principalRegistered(ev):
    user = MemberProperties.get(ev.principal.uuid)
    user.joined = datetime.now()

    if ptah.PTAH_CONFIG.validation and \
            IPrincipalWithEmail.providedBy(ev.principal):
        initiateValidation(ev.principal, get_current_request())


@config.handler(ptah.events.PrincipalRegisteredEvent)
def principalAdded(ev):
    user = MemberProperties.get(ev.principal.uuid)
    user.joined = datetime.now()
    user.validated = True


class ValidationTemplate(mail.MailTemplate):

    subject = 'Activate Your Account'
    template = view.template('ptah.crowd:templates/validate_email.txt')

    def update(self):
        super(ValidationTemplate, self).update()

        self.url = '%s/validateaccount.html?token=%s'%(
            self.request.application_url, self.token)

        principal = self.context
        self.to_address = mail.formataddr((principal.name, principal.email))


view.registerRoute('ptah-principal-validate', '/validateaccount.html')

@view.pyramidView(route='ptah-principal-validate')
def validate(request):
    """Validate account"""
    t = request.GET.get('token')

    data = token.tokenService.get(t)
    if data is not None:
        user = MemberProperties.get(data)
        if user is not None:
            user.validated = True
            token.tokenService.remove(t)
            view.addMessage(request, "Account has been successfully validated.")

            request.registry.notify(
                ptah.events.PrincipalValidatedEvent(
                    ptah.resolve(user.uuid)))

            headers = remember(request, user.uuid)
            raise HTTPFound(location=request.application_url, headers=headers)

    view.addMessage(request, "Can't validate email address.", 'warning')
    raise HTTPFound(location=request.application_url)
