""" mail settings """
import ptah
import os.path
import itertools
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.utils import formatdate, formataddr
from email.header import make_header

from pyramid import renderers
from pyramid.compat import bytes_


class MailGenerator(object):
    """ mail generator """

    def __init__(self, context):
        self._headers = {}
        self.context = context

    def _add_header(self, header, value, encode=False):
        self._headers[header] = (header, value, encode)

    def set_headers(self, message):
        charset = str(self.context.charset)

        extra = list(self.context.get_headers())
        for key, val, encode in itertools.chain(self._headers.values(), extra):
            if encode:
                message[key] = make_header(((val, charset),))
            else:
                message[key] = val

    def get_message(self):
        """ render a mail template """
        context = self.context

        charset = str(context.charset)
        contentType = context.content_type

        mail_body = context.render()
        maintype, subtype = contentType.split('/')

        return MIMEText(mail_body, subtype, charset)

    def get_attachments(self):
        attachments = []

        # attach files
        for data, content_type, filename, disposition in \
                self.context.get_attachments():
            maintype, subtype = content_type.split('/')

            msg = MIMENonMultipart(maintype, subtype)

            msg.set_payload(data)
            if filename:
                msg['Content-Id']=bytes_('<{0}@ptah>'.format(filename),'utf-8')
                msg['Content-Disposition']=bytes_('{0}; filename="{1}"'.format(
                    disposition, filename), 'utf-8')

            encoders.encode_base64(msg)
            attachments.append(msg)

        return attachments

    def message(self, multipart_format='mixed', *args, **kw):
        context = self.context

        # generate message
        message = self.get_message()

        # generate attachments
        attachments = self.get_attachments()
        if attachments:
            # create multipart message
            root = MIMEMultipart(multipart_format)

            # insert headers
            self.set_headers(root)

            # create message with attachments
            related = MIMEMultipart('related')
            related.attach(message)

            for attach in attachments:
                disposition = attach['Content-Disposition']\
                              .decode('utf-8').split(';')[0]
                if disposition == 'attachment':
                    root.attach(attach)
                else:
                    related.attach(attach)

            root.attach(related)
            message = root

        # alternative
        alternatives = self.context.get_alternative()
        if alternatives:
            mainmessage = MIMEMultipart('alternative')
            mainmessage.attach(message)

            for msg in alternatives:
                mainmessage.attach(MailGenerator(msg).message(
                        multipart_format, *args, **kw))

            message = mainmessage

        # default headers
        self._add_header('Subject', context.subject, True)

        self.set_headers(message)
        return message

    def __call__(self, multipart_format='mixed', *args, **kw):
        context = self.context
        message = self.message(multipart_format, *args, **kw)

        message['Date'] = formatdate()
        message['Message-ID'] = context.message_id

        if not message.get('To') and context.to_address:
            message['To'] = context.to_address

        if not message.get('From') and context.from_address:
            message['From'] = formataddr(
                (context.from_name, context.from_address))

        return message


class MailTemplate(object):
    """ mail template with base features """

    subject = ''
    charset = 'utf-8'
    content_type = 'text/plain'
    message_id = None
    template = None

    from_name = ''
    from_address = ''
    to_address = ''
    return_address = ''
    errors_address = ''

    def __init__(self, context, request, **kwargs):
        self.__dict__.update(kwargs)

        self.context = context
        self.request = request
        self.cfg = ptah.get_settings(ptah.CFG_ID_PTAH, request.registry)

        self._files = []
        self._headers = {}
        self._alternative = []

    def add_header(self, header, value, encode=False):
        self._headers[header] = (header, value, encode)

    def has_header(self, header):
        header = header.lower()
        for key in self._headers.keys():
            if key.lower() == header:
                return True

        return False

    def get_headers(self):
        return self._headers.values()

    def add_attachment(self, file_data, content_type,
                       filename, disposition='attachment'):
        self._files.append((file_data, content_type,
                            wrap_filename(filename), disposition))

    def get_attachments(self):
        return self._files

    def add_alternative(self, template):
        self._alternative.append(template)

    def get_alternative(self):
        return self._alternative

    def update(self):
        if not self.from_name:
            self.from_name = self.cfg['email_from_name']
        if not self.from_address:
            self.from_address = self.cfg['email_from_address']

    def render(self):
        kwargs = {'view': self,
                  'context': self.context,
                  'request': self.request}

        return renderers.render(self.template, kwargs, self.request)

    def send(self, email=None, mailer=None, **kw):
        if email:
            self.to_address = email

        message = self(**kw)

        if mailer is None:
            mailer = self.cfg.get('Mailer')

        if mailer is not None:
            mailer.send(message['from'], message['to'], message)

    def __call__(self, **kw):
        for key, value in kw.items():
            if type(value) is tuple:
                self.add_header(key, value[0], value[1])
            else:
                self.add_header(key, value)

        self.update()
        return MailGenerator(self)()


def wrap_filename(f_name):
    dir, f_name = os.path.split(f_name)
    f_name = f_name.split('\\')[-1].split('/')[-1]
    for key in '~,\'':
        f_name = f_name.replace(key, '_')

    return f_name
