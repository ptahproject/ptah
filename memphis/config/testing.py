""" memphis.config tests setup

$Id: testing.py 11802 2011-01-31 06:25:41Z fafhrd91 $
"""
import os, sys, types
from zope import interface, component
from zope.component import getSiteManager
from zope.component import hooks, eventtesting
from zope.component import testing as catesting

from memphis.config import api, meta


class FakeModule(types.ModuleType):
    """A fake module."""

    def __init__(self, dict):
        self.fake_module = True
        for key, val in dict.items():
            setattr(self, key, val)


class FakeModuleGlobs(dict):

    def __setitem__(self, key, val):
        super(FakeModuleGlobs, self).__setitem__(key, val)

        setattr(sys.modules[self['__name__']], key, val)


def setUpTestAsModule(test, name):
    def reGrok():
        for key, val in test.globs.items():
            setattr(sys.modules[name], key, val)
        api.grokkerRegistry.grok(name, sys.modules[name])

    test.globs['__name__'] = name
    test.globs['fake_module'] = True
    test.globs['reGrok'] = reGrok
    test.globs = FakeModuleGlobs(test.globs)
    sys.modules[name] = FakeModule(test.globs)


def tearDownTestAsModule(test):
    del sys.modules[test.globs['__name__']]
    test.globs.clear()


def setUpConfig(test):
    catesting.setUp(test)
    eventtesting.setUp(test)
    hooks.setHooks()
    api.begin()
    api.commit()


def tearDownConfig(test):
    api.cleanUp()
    catesting.tearDown(test)
