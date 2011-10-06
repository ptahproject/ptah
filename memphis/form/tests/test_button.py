import unittest

class TestActions(unittest.TestCase):
    def _makeOne(self, form, request):
        from memphis.form.button import Actions
        return Actions(form, request)

    def test_ctor(self):
        from pyramid.i18n import Localizer
        request = DummyRequest()
        form = DummyForm()
        inst = self._makeOne(form, request)
        self.assertEqual(inst.form, form)
        self.assertEqual(inst.request, request)
        self.assertEqual(inst.localizer.__class__, Localizer)

class DummyRequest(object):
    def __init__(self):
        self.params = {}
        self.cookies = {}
        
class DummyForm(object):
    prefix = 'prefix'
    def __init__(self):
        self.buttons = {}
    def getParams(self):
        return None
    def getContent(self):
        return None

