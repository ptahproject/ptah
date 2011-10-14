""" account validation/suspending """
from datetime import timedelta, datetime
from memphis import view, config
from pyramid.security import remember
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import token, mail

from settings import CROWD
from memberprops import get_properties, query_properties

TOKEN_TYPE = token.TokenType(
    'cd51f14e9b2842608ccadf1a240046c1', timedelta(hours=24))


def initiate_email_validation(email, principal, request):
    """ initiate principal email validation """
    t = token.service.generate(TOKEN_TYPE, principal.uri)
    template = ValidationTemplate(principal, request, email=email, token = t)
    template.send()


@ptah.register_auth_checker
def validationAndSuspendedChecker(info):
    props = get_properties(info.principal.uri)
    if props.suspended:
        info.message = u'Account is suspended.'
        info.arguments['suspended'] = True
        return False

    if props.validated:
        return True

    if not CROWD['validation']:
        return True

    if CROWD['allow-unvalidated'] or props.validated:
        return True

    info.message = u'Account is not validated.'
    info.arguments['validation'] = False
    return False


@config.subscriber(ptah.events.PrincipalRegisteredEvent)
def principalRegistered(ev):
    props = get_properties(ev.principal.uri)
    props.joined = datetime.now()

    if not CROWD['validation']:
        props.validated = True


@config.subscriber(ptah.events.PrincipalAddedEvent)
def principalAdded(ev):
    props = get_properties(ev.principal.uri)
    props.joined = datetime.now()
    props.validated = True


class ValidationTemplate(mail.MailTemplate):

    subject = 'Activate Your Account'
    template = view.template('ptah_crowd:templates/validate_email.txt')

    def update(self):
        super(ValidationTemplate, self).update()

        self.url = '%s/validateaccount.html?token=%s'%(
            self.request.application_url, self.token)

        principal = self.context
        self.to_address = mail.formataddr((principal.name, self.email))


view.register_route('ptah-principal-validate', '/validateaccount.html')

@view.pyramidview(route='ptah-principal-validate')
def validate(request):
    """Validate account"""
    t = request.GET.get('token')

    data = token.service.get(t)
    if data is not None:
        props = query_properties(data)
        if props is not None:
            props.validated = True
            token.service.remove(t)
            view.add_message(request, "Account has been successfully validated.")

            config.notify(
                ptah.events.PrincipalValidatedEvent(ptah.resolve(props.uri)))

            headers = remember(request, props.uri)
            raise HTTPFound(location=request.application_url, headers=headers)

    view.add_message(request, "Can't validate email address.", 'warning')
    raise HTTPFound(location=request.application_url)
