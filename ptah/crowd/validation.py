""" account validation """
from datetime import timedelta
from memphis import view
from webob.exc import HTTPFound
from pyramid.security import remember

from ptah import token, mail
from ptah.crowd.models import User


TOKEN_TYPE = token.registerTokenType(
    '5cfcb3e2-e93f-42f7-9d1c-59077952bd72', timedelta(hours=24))


def initiateValidation(principal, request):
    t = token.tokenService.generate(TOKEN_TYPE, principal.id)
    template = ValidationTemplate(principal, request)
    template.token = token
    template.send()


class ValidationTemplate(mail.MailTemplate):

    subject = 'Activate Your Account'
    template = view.template('ptah.crowd:templates/validate_email.txt')

    def update(self):
        super(ValidationTemplate, self).update()

        request = self.request

        self.url = '%s/validateaccount.html?token=%s'%(
            request.application_url, self.token)

        principal = self.context

        self.to_address = mail.formataddr((principal.name, principal.login))


view.registerRoute(
    'ptah-crowd-validate', '/validateaccount.html', view.DefaultRoot)

@view.pyramidView(route='ptah-crowd-validate')
def validate(request):
    t = request.GET.get('token')

    data = token.tokenService.get(TOKEN_TYPE, t)
    if data is not None:
        user = User.getById(data)
        if user is not None:
            user.validated = True
            token.tokenService.remove(t)

            headers = remember(request, user.login)
            raise HTTPFound(location=request.application_url, headers=headers)

    view.addMessage(request, "Can't validate email address.", 'warning')
    raise HTTPFound(location=request.application_url)
