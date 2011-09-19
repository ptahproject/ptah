""" pagelet tests """
import sys, unittest
from zope import interface, component
from pyramid.httpexceptions import HTTPNotFound
from memphis import config, view
from memphis.config import api
from memphis.view.pagelet import IPagelet, Pagelet, PageletType, renderPagelet

from base import Base


class TestPagelet(Base):

    def _setup_memphis(self):
        pass

    def test_pagelettype_register(self):
        class ITestPagelet(interface.Interface):
            pass

        view.pageletType('test', Context)
        self._init_memphis()

        from memphis.view.pagelet import ptypes

        self.assertTrue('test' in ptypes)

        pt = ptypes['test']
        self.assertTrue(isinstance(pt, PageletType))
        self.assertEqual(pt.name, 'test')
        self.assertEqual(pt.context, Context)

    def test_pagelet_register_errors(self):
        class TestPagelet(view.Pagelet):
            pass

        view.pageletType('test1', Context)
        view.pageletType('test2', Context)

        view.registerPagelet('test1', Context, TestPagelet)
        view.registerPagelet('test2', Context, TestPagelet)

        self.assertRaises(ValueError, self._init_memphis)

    def test_pagelet_register_nopt(self):
        class ITestPagelet(interface.Interface):
            pass

        class TestPagelet(view.Pagelet):
            pass

        view.registerPagelet(ITestPagelet, Context, TestPagelet)

        self.assertRaises(LookupError, self._init_memphis)

    def test_pagelet_register(self):
        class TestPagelet(view.Pagelet):
            def render(self):
                return 'test pagelet'

        view.pageletType('test', Context)
        view.registerPagelet('test', Context, TestPagelet)
        self._init_memphis()

        self.assertEqual(
            renderPagelet('test', Context(), self.request), 'test pagelet')

    def test_pagelet_register_declarative(self):
        global TestPagelet

        view.pageletType('pt', Context)

        class TestPagelet(view.Pagelet):
            view.pagelet('pt')

            def render(self):
                return 'test'

        self._init_memphis()

        self.assertEqual(renderPagelet('pt', Context(), self.request), 'test')

    def test_pagelet_register_with_template(self):
        class TestPagelet(view.Pagelet):
            pass

        def template(*args, **kw):
            keys = kw.keys()
            keys.sort()
            return '|'.join(keys)

        view.pageletType('test', Context)
        view.registerPagelet('test', klass=TestPagelet, template = template)
        self._init_memphis()

        self.assertEqual(
            renderPagelet('test', Context(), self.request),
            'context|format|request|view')

    def test_pagelet_register_without_class(self):
        view.pageletType('test', Context)
        view.registerPagelet('test', Context)
        self._init_memphis()

        pagelet = component.getMultiAdapter(
            (Context(), self.request), IPagelet, 'test')

        self.assertTrue(isinstance(pagelet, Pagelet))
        self.assertEqual(str(pagelet.__class__),
                         "<class 'memphis.view.pagelet.Pagelet None'>")

    def test_pagelet_register_with_not_Pagelet_class(self):
        class TestPagelet(object):
            pass

        view.pageletType('test', Context)
        view.registerPagelet('test', Context, TestPagelet)
        self._init_memphis()

        pagelet = component.getMultiAdapter(
            (Context(), self.request), IPagelet, 'test')

        self.assertTrue(isinstance(pagelet, Pagelet))
        self.assertTrue(isinstance(pagelet, TestPagelet))

    def test_pagelet_renderpagelet_not_found(self):
        self.assertRaises(
            HTTPNotFound,
            renderPagelet, 'test', Context(), self.request)

    def test_pagelet_render_with_exception(self):
        class TestPagelet(view.Pagelet):
            def render(self):
                raise ValueError('Unknown')

        view.pageletType('test', Context)
        view.registerPagelet('test', Context, TestPagelet)
        self._init_memphis()

        self.assertRaises(
            ValueError,
            renderPagelet, 'test', Context(), self.request)

    def test_pagelet_render_additional_params_to_template(self):
        class TestPagelet(view.Pagelet):
            def update(self):
                return {'param1': 1, 'param2': 2}

        def template(*args, **kw):
            keys = kw.keys()
            keys.sort()
            return '|'.join(keys)

        view.pageletType('test', Context)
        view.registerPagelet('test', klass=TestPagelet, template = template)
        self._init_memphis()

        self.assertTrue(
            'param1|param2|' in renderPagelet('test', Context(), self.request))

    def test_pagelet_View_pagelet(self):
        class TestPagelet(view.Pagelet):
            def render(self):
                return 'test pagelet'

        view.pageletType('test', Context)
        view.registerPagelet('test', Context, TestPagelet)
        self._init_memphis()

        base = view.View(None, self.request)

        # pageletType is string
        self.assertEqual(base.pagelet('unknown', Context()), '')
        self.assertEqual(base.pagelet('test', Context()), 'test pagelet')

        # by default use view context
        base.context = Context()
        self.assertEqual(base.pagelet('test'), 'test pagelet')


    def test_pagelet_View_pagelet_with_error(self):
        class TestPagelet(view.Pagelet):
            def render(self):
                raise ValueError('Error')

        view.pageletType('test', Context)
        view.registerPagelet('test', Context, TestPagelet)
        self._init_memphis()

        base = view.View(None, self.request)
        self.assertEqual(base.pagelet('test', Context()), '')


class Context(object):
    pass
