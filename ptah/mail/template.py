""" base MailTemplate class """
import os.path
from email.Utils import formataddr
from ptah.mail.mail import MAIL
from ptah.mail.generator import MailGenerator


class MailTemplate(object):
    """ mail template with base features """

    subject = u''
    charset = u'utf-8'
    contentType = u'text/plain'
    messageId = None
    template = None

    from_name = ''
    from_address = ''
    to_address = ''
    return_address = ''
    errors_address = ''


    def __init__(self, context, request):
        self.context = context
        self.request = request

        self._files = []
        self._headers = {}
        self._alternative = []

    def addHeader(self, header, value, encode=False):
        self._headers[header] = (header, value, encode)

    def hasHeader(self, header):
        header = header.lower()
        for key in self._headers.keys():
            if key.lower() == header:
                return True

        return False

    def getHeaders(self):
        return self._headers.values()

    def addAttachment(self, file_data, content_type,
                      filename, disposition='attachment'):
        self._files.append((file_data, content_type,
                            wrap_filename(filename), disposition))

    def getAttachments(self):
        return self._files

    def addAlternative(self, template):
        self._alternative.append(template)

    def getAlternative(self):
        return self._alternative

    def update(self):
        self.from_name = MAIL.from_name
        self.from_address = MAIL.from_address

    def render(self):
        kwargs = {'view': self,
                  'context': self.context,
                  'request': self.request,
                  'nothing': None}

        return self.template(**kwargs)

    def send(self, emails=None, **kw):
        if emails:
            self.to_address = emails

        message = self(**kw)

        MAIL.Mailer.send(message['from'], message['to'], message)

    def __call__(self, **kw):
        for key, value in kw.items():
            if type(value) is tuple:
                self.addHeader(key, value[0], value[1])
            else:
                self.addHeader(key, value)

        self.update()
        return MailGenerator(self)()


def wrap_filename(f_name):
    dir, f_name = os.path.split(f_name)
    f_name = f_name.split('\\')[-1].split('/')[-1]
    for key in '~,\'':
        f_name = f_name.replace(key, '_')

    return f_name
