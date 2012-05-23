from zope.interface import implementedBy
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationError, ConfigurationConflictError
from pyramid.httpexceptions import HTTPNotFound

import ptah
from ptah.testing import unittest
try:
    import pyramid_sockjs
    has_sockjs = True
except ImportError:
    has_sockjs = False


@unittest.skipUnless(has_sockjs, 'No pyramid_sockjs')
class TestForm(ptah.PtahTestCase):

    def _make_p(self):
        from ptah import sockjs

        class P(sockjs.Protocol):
            def __init__(self, request):
                self.request = request
                self.data = []

            def send(self, tp, data, **kw):
                self.data.append((tp, data))

        return P

    def _make_form(self):
        from ptah import sockjs

        class F(sockjs.Form):
            fields = ptah.form.Fieldset(
                ptah.form.TextField('name'))

            err = False

            @ptah.form.button('Submit', name='submit')
            def test_Action(self):
                if self.err:
                    return ['Error']
                self._action = 1

        return F

    def test_ctor(self):
        from ptah import sockjs

        p = self._make_p()(self.request)
        form = sockjs.Form('test', {'id':'12345'}, p)

        self.assertEqual(form.mtype, 'test')
        self.assertEqual(form.params, {'id':'12345'})
        self.assertIs(form.protocol, p)

    def test_close(self):
        from ptah import sockjs

        p = self._make_p()(self.request)
        form = sockjs.Form('test', {'id':'12345'}, p)
        form.close()

        self.assertEqual(p.data[-1][0], 'test')
        self.assertEqual(p.data[-1][1], {'__close__': True})

    def test_close_with_message(self):
        from ptah import sockjs

        p = self._make_p()(self.request)
        form = sockjs.Form('test', {'id':'12345'}, p)
        form.close('Close message')

        self.assertEqual(p.data[-1][0], 'test')
        self.assertEqual(p.data[-1][1]['__close__'], True)
        self.assertIn('Close message', p.data[-1][1]['message'])

    def test_render(self):
        from ptah import sockjs

        p = self._make_p()(self.request)
        form = self._make_form()('test', {'id':'12345'}, p)
        form.update()

        data = form.render()

        self.assertEqual(data['name'], 'form')
        self.assertEqual(data['actions'][0]['name'], 'submit')
        self.assertEqual(
            data['fieldsets'][0]['widgets'][0]['id'], 'form-widgets-name')

        # with error
        form.errors = ['Error']
        data = form.render()

        self.assertIn('errors', data)

        # extra data
        def get_msg_data():
            return {'extra': '12345'}

        form.get_msg_data = get_msg_data
        data = form.render()
        self.assertEqual(data['extra'], '12345')

    def test_call(self):
        from ptah import sockjs

        P = self._make_p()
        Form = self._make_form()

        p = P(self.request)
        form = Form('test', {}, p)
        form()

        self.assertEqual(len(p.data), 1)
        self.assertEqual(p.data[0][0], 'test')

        # unknown action
        p = P(self.request)
        form = Form('test', {'__action__': 'unknown'}, p)
        form()
        self.assertEqual(len(p.data), 1)

        # action with error
        p = P(self.request)
        form = Form('test', {'__action__': 'submit'}, p)
        form.err = True
        form()
        self.assertIn('errors', p.data[0][1])

        # action
        p = P(self.request)
        form = Form('test', {'__action__': 'submit'}, p)
        form()
        self.assertEqual(len(p.data), 0)
        self.assertEqual(form._action, 1)

        # action with different payload format
        p = P(self.request)
        form = Form('test', [['__action__', 'submit']], p)
        form()
        self.assertEqual(len(p.data), 0)
        self.assertEqual(form._action, 1)

    def test_validate(self):
        from ptah import sockjs

        P = self._make_p()
        Form = self._make_form()

        # unknown action
        p = P(self.request)
        form = Form('test', {'__validate__': True}, p)
        form.err = True
        form()
        #print p.data
        self.assertEqual(len(p.data), 1)
