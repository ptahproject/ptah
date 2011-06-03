""" memphis.config tests setup """
import os, sys, types
from zope import interface, component
from zope.component import getSiteManager
from zope.component import hooks, eventtesting
from zope.component import testing as catesting

from memphis.config import api, meta, directives


class FakeModule(types.ModuleType):
    """A fake module."""

    __fake_module__ = True

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
    directives.action.immediately = True


def tearDownConfig(test):
    api.cleanUp()
    catesting.tearDown(test)
    directives.action.immediately = False
