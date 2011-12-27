from ptah.testing import PtahTestCase, TestCase


class TestButton(PtahTestCase):

    def test_ctor(self):
        from ptah import form

        btn = form.Button(name='test', actionName='action',
                          actype = form.AC_PRIMARY)

        self.assertEqual(btn.name, 'test')
        self.assertEqual(btn.title, 'Test')
        self.assertEqual(btn.actype, form.AC_PRIMARY)
        self.assertEqual(repr(btn), '<Button "test" : "Test">')

    def test_bind(self):
        from ptah import form

        btn = form.Button(name='test', actionName='action',
                          actype = form.AC_PRIMARY)

        params = {}
        context = object()
        request = DummyRequest()

        widget = btn.bind('test.', params, context, request)

        self.assertIsNot(btn, widget)
        self.assertIs(widget.context, context)
        self.assertIs(widget.request, request)
        self.assertIs(widget.params, params)
        self.assertEqual(widget.id, 'test-test')
        self.assertEqual(widget.name, 'test.test')
        self.assertEqual(widget.klass, 'btn primary')

    def test_activated(self):
        from ptah import form

        btn = form.Button(name='test', actionName='action',
                          actype = form.AC_PRIMARY)
        params = {'button.unkown': 'true'}
        context = object()
        request = DummyRequest()

        widget = btn.bind('button.', params, context, request)

        self.assertFalse(widget.activated())

        widget.params = {'button.test': 'true'}
        self.assertTrue(widget.activated())

    def test_render(self):
        from ptah import form

        btn = form.Button(name='test', actionName='action',
                          actype = form.AC_PRIMARY)
        params = {}
        context = object()
        request = DummyRequest()

        widget = btn.bind('test.', params, context, request)
        self.assertEqual(
            widget.render().strip(),
            """<input id="test-test" name="test.test" class="btn primary" value="Test" type="submit" />""")

    def test_execute(self):
        from ptah import form

        btn = form.Button(name='test', actionName='action')

        class Test(object):
            def action(self):
                return 'Action executed'

        self.assertRaises(AttributeError, btn, object())
        self.assertEqual(btn(Test()), 'Action executed')

        btn = form.Button(name='test', action=Test.action,
                          actype = form.AC_PRIMARY)
        self.assertEqual(btn(Test()), 'Action executed')

        btn = form.Button(name='test')
        self.assertRaises(TypeError, btn, Test())


class TestButtons(TestCase):

    def test_ctor(self):
        from ptah import form

        btn1 = form.Button(name='test1', actionName='action')
        btn2 = form.Button(name='test2', actionName='action')

        btns = form.Buttons()
        self.assertFalse(bool(btns))

        btns = form.Buttons(btn1, btn2)
        self.assertEqual(list(btns.keys()), [btn1.name, btn2.name])
        self.assertEqual(list(btns.values()), [btn1, btn2])

        btns = form.Buttons(btn1)
        self.assertEqual(list(btns.keys()), [btn1.name])

        btns = form.Buttons(btn2, btns)
        self.assertEqual(list(btns.keys()), [btn2.name, btn1.name])
        self.assertEqual(list(btns.values()), [btn2, btn1])

    def test_add(self):
        from ptah import form

        btn1 = form.Button(name='test1', actionName='action')
        btn2 = form.Button(name='test2', actionName='action')

        btns = form.Buttons(btn1)

        btns.add(btn2)
        self.assertEqual(list(btns.keys()), [btn1.name, btn2.name])
        self.assertEqual(list(btns.values()), [btn1, btn2])

    def test_add_duplicate(self):
        from ptah import form

        btn1 = form.Button(name='test1', actionName='action')
        btn2 = form.Button(name='test1', actionName='action')

        btns = form.Buttons(btn1)

        self.assertRaises(ValueError, btns.add, btn2)

    def test_add_action(self):
        from ptah import form

        btns = form.Buttons()

        btn1 = btns.add_action('Test action')

        self.assertIsInstance(btn1, form.Button)
        self.assertEqual(list(btns.keys()), [btn1.name])
        self.assertEqual(list(btns.values()), [btn1])

    def test_iadd(self):
        from ptah import form

        btn1 = form.Button(name='test1', actionName='action')
        btn2 = form.Button(name='test2', actionName='action')

        btns1 = form.Buttons(btn1)
        btns2 = form.Buttons(btn2)

        btns = btns1 + btns2
        self.assertEqual(list(btns.keys()), [btn1.name, btn2.name])
        self.assertEqual(list(btns.values()), [btn1, btn2])


class TestButtonDecorator(TestCase):

    def test_decorator(self):
        from ptah import form

        class MyForm(object):
            @form.button('Test button')
            def handler(self):
                """ """

        self.assertEqual(len(MyForm.buttons), 1)

        btn = list(MyForm.buttons.values())[0]
        self.assertEqual(btn.title, 'Test button')
        self.assertEqual(btn.actionName, 'handler')

    def test_decorator_multiple(self):
        from ptah import form

        class MyForm(object):
            @form.button('Test button')
            def handler1(self):
                """ """
            @form.button('Test button2')
            def handler2(self):
                """ """

        self.assertEqual(len(MyForm.buttons), 2)

        btn1 = list(MyForm.buttons.values())[0]
        btn2 = list(MyForm.buttons.values())[1]
        self.assertEqual(btn1.actionName, 'handler1')
        self.assertEqual(btn2.actionName, 'handler2')

    def test_create_id(self):
        import binascii
        from ptah.form.button import create_btn_id

        self.assertEqual(create_btn_id('Test'), 'test')
        self.assertEqual(create_btn_id('Test title'),
                         binascii.hexlify('Test title'.encode('utf-8')))


class TestActions(TestCase):

    def _makeOne(self, form, request):
        from ptah.form.button import Actions
        return Actions(form, request)

    def test_ctor(self):
        request = DummyRequest()
        form = DummyForm()
        inst = self._makeOne(form, request)
        self.assertEqual(inst.form, form)
        self.assertEqual(inst.request, request)

    def test_update(self):
        from ptah import form

        request = DummyRequest()
        tform = DummyForm()

        def disabled(form):
            return False

        res = {}
        def action1(form):
            res['action1'] = True
        def action2(form): # pragma: no cover
            res['action2'] = True

        btn1 = form.Button(name='test1', action=action1)
        btn2 = form.Button(name='test2', action=action2, condition = disabled)
        tform.buttons = form.Buttons(btn1, btn2)

        actions = self._makeOne(tform, request)
        actions.update()

        self.assertEqual(list(actions.keys()), [btn1.name])
        self.assertEqual(actions[btn1.name].name, 'form.buttons.test1')

        actions.execute()
        self.assertEqual(res, {})

        params = {'form.buttons.test1': 'true',
                  'form.buttons.test2': 'true'}
        tform.params = params
        actions.update()
        actions.execute()
        self.assertEqual(res, {'action1': True})


class DummyRequest(object):
    def __init__(self):
        self.params = {}
        self.cookies = {}


class DummyForm(object):
    prefix = 'form.'
    params = {}
    def __init__(self):
        self.buttons = {}
    def form_params(self):
        return self.params
