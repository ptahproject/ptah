""" pagelet tests """
import sys, unittest
from webob.exc import HTTPNotFound
from zope import interface, component
from memphis import config, view
from memphis.config import api
from memphis.view.pagelet import Pagelet, PageletType, renderPagelet

from base import Base

       
class TestPagelet(Base):

    def _setup_memphis(self):
        pass

    def test_pagelettype_register(self):
        class ITestPagelet(interface.Interface):
            pass

        view.registerPageletType('test', ITestPagelet, Context)
        self._init_memphis()
        
        pt = component.getUtility(view.IPageletType, 'test')
        self.assertTrue(isinstance(pt, PageletType))
        self.assertEqual(pt.name, 'test')
        self.assertEqual(pt.type, ITestPagelet)
        self.assertEqual(pt.context, Context)
        self.assertEqual(
            ITestPagelet.getTaggedValue('memphis.view.pageletType'), pt)

    def test_pagelettype_register_declarative(self):
        global ITestPage

        class ITestPagelet(interface.Interface):
            view.pageletType('test2', Context)

        self._init_memphis()
                    
        pt = component.getUtility(view.IPageletType, 'test2')
        self.assertTrue(isinstance(pt, PageletType))
        self.assertEqual(pt.name, 'test2')
        self.assertEqual(pt.type, ITestPagelet)
        self.assertEqual(pt.context, Context)

    def test_pagelet_register_errors(self):
        class ITestPagelet1(interface.Interface):
            pass
        class ITestPagelet2(interface.Interface):
            pass

        class TestPagelet(view.Pagelet):
            pass

        view.registerPageletType('test1', ITestPagelet1, Context)
        view.registerPageletType('test2', ITestPagelet2, Context)

        view.registerPagelet(ITestPagelet1, Context, TestPagelet)
        view.registerPagelet(ITestPagelet2, Context, TestPagelet)

        self.assertRaises(ValueError, self._init_memphis)
 
    def test_pagelet_register_nopt(self):
        class ITestPagelet(interface.Interface):
            pass

        class TestPagelet(view.Pagelet):
            pass

        view.registerPagelet(ITestPagelet, Context, TestPagelet)

        self.assertRaises(LookupError, self._init_memphis)

    def test_pagelet_register(self):
        class ITestPagelet(interface.Interface):
            pass

        class TestPagelet(view.Pagelet):
            def render(self):
                return 'test pagelet'

        view.registerPageletType('test', ITestPagelet, Context)
        view.registerPagelet(ITestPagelet, Context, TestPagelet)
        self._init_memphis()

        self.assertEqual(
            renderPagelet(ITestPagelet, Context(), self.request),
            'test pagelet')

    def test_pagelet_register_declarative(self):
        global ITestPagelet, TestPagelet

        class ITestPagelet(interface.Interface):
            view.pageletType('test', Context)

        class TestPagelet(view.Pagelet):
            view.pagelet(ITestPagelet)

            def render(self):
                return 'test'

        self._init_memphis()

        self.assertEqual(
            renderPagelet(ITestPagelet, Context(), self.request), 'test')

    def test_pagelet_register_with_template(self):
        class ITestPagelet(interface.Interface):
            pass

        class TestPagelet(view.Pagelet):
            pass

        def template(*args, **kw):
            keys = kw.keys()
            keys.sort()
            return '|'.join(keys)

        view.registerPageletType('test', ITestPagelet, Context)
        view.registerPagelet(ITestPagelet, klass=TestPagelet,
                             template = template)
        self._init_memphis()

        self.assertEqual(
            renderPagelet(ITestPagelet, Context(), self.request),
            'context|format|nothing|request|template|view')

    def test_pagelet_register_without_class(self):
        class ITestPagelet(interface.Interface):
            pass

        view.registerPageletType('test', ITestPagelet, Context)
        view.registerPagelet(ITestPagelet, Context)
        self._init_memphis()

        pagelet = component.getMultiAdapter(
            (Context(), self.request), ITestPagelet)
    
        self.assertTrue(isinstance(pagelet, Pagelet))
        self.assertEqual(str(pagelet.__class__),
                         "<class 'memphis.view.pagelet.Pagelet None'>")

    def test_pagelet_register_with_not_Pagelet_class(self):
        class ITestPagelet(interface.Interface):
            pass

        class TestPagelet(object):
            pass

        view.registerPageletType('test', ITestPagelet, Context)
        view.registerPagelet(ITestPagelet, Context, TestPagelet)
        self._init_memphis()

        pagelet = component.getMultiAdapter(
            (Context(), self.request), ITestPagelet)
    
        self.assertTrue(isinstance(pagelet, Pagelet))
        self.assertTrue(isinstance(pagelet, TestPagelet))

    def test_pagelet_renderpagelet_not_found(self):
        class ITestPagelet(interface.Interface):
            pass
        
        self.assertRaises(
            HTTPNotFound, 
            renderPagelet, ITestPagelet, Context(), self.request)

    def test_pagelet_render_with_exception(self):
        class ITestPagelet(interface.Interface):
            pass

        class TestPagelet(view.Pagelet):
            def render(self):
                raise ValueError('Unknown')

        view.registerPageletType('test', ITestPagelet, Context)
        view.registerPagelet(ITestPagelet, Context, TestPagelet)
        self._init_memphis()

        self.assertRaises(
            ValueError,
            renderPagelet, ITestPagelet, Context(), self.request)

    def test_pagelet_render_additional_params_to_template(self):
        class ITestPagelet(interface.Interface):
            pass

        class TestPagelet(view.Pagelet):
            def update(self):
                return {'param1': 1, 'param2': 2}

        def template(*args, **kw):
            keys = kw.keys()
            keys.sort()
            return '|'.join(keys)

        view.registerPageletType('test', ITestPagelet, Context)
        view.registerPagelet(ITestPagelet, klass=TestPagelet,
                             template = template)
        self._init_memphis()

        self.assertTrue(
            'param1|param2|' in 
            renderPagelet(ITestPagelet, Context(), self.request))

    def test_pagelet_View_pagelet(self):
        class ITestPagelet(interface.Interface):
            pass

        class TestPagelet(view.Pagelet):
            def render(self):
                return 'test pagelet'

        view.registerPageletType('test', ITestPagelet, Context)
        view.registerPagelet(ITestPagelet, Context, TestPagelet)
        self._init_memphis()

        base = view.View(None, self.request)

        # pageletType is string
        self.assertEqual(base.pagelet('unknown', Context()), '')
        self.assertEqual(base.pagelet('test', Context()), 'test pagelet')

        # pageletType is interface
        self.assertEqual(base.pagelet(ITestPagelet, Context()), 'test pagelet')

        # by default use view context
        base.context = Context()
        self.assertEqual(base.pagelet(ITestPagelet), 'test pagelet')
        

    def test_pagelet_View_pagelet_with_error(self):
        class ITestPagelet(interface.Interface):
            pass

        class TestPagelet(view.Pagelet):
            def render(self):
                raise ValueError('Error')

        view.registerPageletType('test', ITestPagelet, Context)
        view.registerPagelet(ITestPagelet, Context, TestPagelet)
        self._init_memphis()

        base = view.View(None, self.request)
        self.assertEqual(base.pagelet(ITestPagelet, Context()), '')


class Context(object):
    pass
