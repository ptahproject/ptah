from ptah import view, mail
from pyramid.testing import DummyRequest

from base import Base


class Content(object):
    pass


class TestMailTemplate(Base):

    def _make_one(self):
        from ptah.mail import MailTemplate

        class MyMailTemplate(MailTemplate):
            template = view.template('test_mail_tmpl.pt')
            subject = 'Test subject'
            charset = 'utf-8'
            content_type = 'text/html'

        return MyMailTemplate

    def test_mailtmpl_ctor(self):
        tmpl = mail.MailTemplate(Content(), DummyRequest(),
                                 testattr = 'testattr')

        self.assertEqual(tmpl.testattr, 'testattr')

    def test_mailtmpl_basics(self):
        self._init_ptah()

        cls = self._make_one()
        cls.message_id = 'message id'

        tmpl = cls(Content(), DummyRequest())()

        self.assertEqual(
            tmpl['Content-Type'], 'text/html; charset="utf-8"')
        self.assertEqual(
            tmpl['Content-Transfer-Encoding'], 'base64')
        self.assertEqual(
            tmpl['Subject'], '=?utf-8?q?Test_subject?=')
        self.assertEqual(
            tmpl['Message-ID'], 'message id')
        self.assertEqual(
            tmpl['From'], 'Site administrator <administrator@localhost.org>')

    def test_mailtmpl_from(self):
        self._init_ptah()

        cls = self._make_one()

        cls.from_name = 'Test'
        cls.from_address = 'ptah@ptahproject.com'

        tmpl = cls(Content(), DummyRequest())()
        self.assertEqual(tmpl['From'], 'Test <ptah@ptahproject.com>')

    def test_mailtmpl_to(self):
        self._init_ptah()

        cls = self._make_one()

        cls.to_address = 'ptah@ptahproject.com'

        tmpl = cls(Content(), DummyRequest())()
        self.assertEqual(tmpl['To'], 'ptah@ptahproject.com')

    def test_mailtmpl_headers(self):
        self._init_ptah()

        cls = self._make_one()

        tmpl = cls(Content(), DummyRequest())
        self.assertFalse(tmpl.has_header('X-Mailer'))

        tmpl.add_header('X-Mailer', 'ptah')
        self.assertTrue(tmpl.has_header('X-Mailer'))

        msg = tmpl()
        self.assertEqual(msg['X-Mailer'], 'ptah')

    def test_mailtmpl_headers_encoding(self):
        self._init_ptah()

        cls = self._make_one()

        tmpl = cls(Content(), DummyRequest())
        tmpl.add_header('X-Mailer', 'ptah', True)

        msg = tmpl()
        self.assertEqual(msg['X-Mailer'], '=?utf-8?q?ptah?=')

    def test_mailtmpl_headers_gen(self):
        self._init_ptah()

        cls = self._make_one()
        tmpl = cls(Content(), DummyRequest())

        msg = tmpl(**{'X-Mailer': 'ptah'})
        self.assertEqual(msg['X-Mailer'], 'ptah')

        msg = tmpl(**{'X-Mailer': ('ptah', True)})
        self.assertEqual(str(msg['X-Mailer']), '=?utf-8?q?ptah?=')

    def test_mailtmpl_attachment(self):
        self._init_ptah()

        cls = self._make_one()
        tmpl = cls(Content(), DummyRequest())
        self.assertEqual(tmpl.get_attachments(), [])

        tmpl.add_attachment('File data', 'text/plain', 'file.txt')
        self.assertEqual(
            tmpl.get_attachments(),
            [('File data', 'text/plain', 'file.txt', 'attachment')])

        msg = tmpl()
        payload = msg.get_payload()

        self.assertTrue(msg.is_multipart())
        self.assertEqual(
            payload[0]['Content-Id'], '<file.txt@ptah>')
        self.assertEqual(
            payload[0]['Content-Disposition'],
            'attachment; filename="file.txt"')

    def test_mailtmpl_attachment_inline(self):
        self._init_ptah()

        cls = self._make_one()
        tmpl = cls(Content(), DummyRequest())
        self.assertEqual(tmpl.get_attachments(), [])

        tmpl.add_attachment('File data', 'text/plain', 'file.txt', 'inline')
        self.assertEqual(
            tmpl.get_attachments(),
            [('File data', 'text/plain', 'file.txt', 'inline')])

        msg = tmpl()
        payload = msg.get_payload()[0]
        payload = payload.get_payload()[-1]

        self.assertEqual(
            payload['Content-Disposition'],
            'inline; filename="file.txt"')

    def test_mailtmpl_alternative(self):
        self._init_ptah()

        cls = self._make_one()

        tmpl = cls(Content(), DummyRequest())
        tmpl.add_header('x-tmpl', 'Template1')
        tmpl2 = cls(Content(), DummyRequest())
        tmpl2.add_header('x-tmpl', 'Template2')

        tmpl.add_alternative(tmpl2)
        self.assertEqual(tmpl.get_alternative(), [tmpl2])

        msg = tmpl()

        payload = msg.get_payload()
        self.assertEqual(msg['x-tmpl'], 'Template1')
        self.assertEqual(payload[1]['x-tmpl'], 'Template2')

    def test_mailtmpl_send(self):
        from ptah.settings import MAIL

        self._init_ptah()

        cls = self._make_one()
        tmpl = cls(Content(), DummyRequest())

        data = []
        class Mailer(object):

            def send(self, frm, to, msg):
                data.append((frm, to, msg))

        MAIL.Mailer = Mailer()

        tmpl.send()

        self.assertEqual(
            data[0][0], 'Site administrator <administrator@localhost.org>')
        self.assertEqual(
            data[0][1], None)
        self.assertIn('From: Site administrator <administrator@localhost.org>',
                      data[0][2].as_string())

        tmpl.send('test@ptahproject.org')
        self.assertEqual(data[-1][1], 'test@ptahproject.org')

        del MAIL.Mailer
