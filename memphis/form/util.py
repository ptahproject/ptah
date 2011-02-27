##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Utilities helpful to the package.

$Id: util.py 11744 2011-01-28 09:15:15Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import re
import types
import string
import zope.interface
import zope.contenttype

from memphis.form import interfaces
from memphis.form.interfaces import MessageFactory as _


_identifier = re.compile('[A-Za-z][a-zA-Z0-9_]*$')

def createId(name):
    if _identifier.match(name):
        return str(name).lower()
    return name.encode('utf-8').encode('hex')


_acceptableChars = string.letters + string.digits + '_-'

def createCSSId(name):
    return str(''.join(((char in _acceptableChars and char) or
                         char.encode('utf-8').encode('hex'))
                        for char in name))


classTypes = type, types.ClassType

def getSpecification(spec, force=False):
    """Get the specification of the given object.

    If the given object is already a specification acceptable to the component
    architecture, it is simply returned. This is true for classes
    and specification objects (which includes interfaces).

    In case of instances, an interface is generated on the fly and tagged onto
    the object. Then the interface is returned as the specification.
    """
    # If the specification is an instance, then we do some magic.
    if (force or
        (spec is not None and
         not zope.interface.interfaces.ISpecification.providedBy(spec)
         and not isinstance(spec, classTypes)) ):

        # Step 1: Calculate an interface name
        ifaceName = 'IGeneratedForObject_%i' %hash(spec)

        # Step 2: Find out if we already have such an interface
        existingInterfaces = [
                i for i in zope.interface.directlyProvidedBy(spec)
                    if i.__name__ == ifaceName
            ]

        # Step 3a: Return an existing interface if there is one
        if len(existingInterfaces) > 0:
            spec = existingInterfaces[0]
        # Step 3b: Create a new interface if not
        else:
            iface = zope.interface.interface.InterfaceClass(ifaceName)
            zope.interface.alsoProvides(spec, iface)
            spec = iface
    return spec


def expandPrefix(prefix):
    """Expand prefix string by adding a trailing period if needed.

    expandPrefix(p) should be used instead of p+'.' in most contexts.
    """
    if prefix and not prefix.endswith('.'):
        return prefix + '.'
    return prefix


def getWidgetById(form, id):
    """Get a widget by it's rendered DOM element id."""
    # convert the id to a name
    name = id.replace('-', '.')
    prefix = form.prefix + form.widgets.prefix
    if not name.startswith(prefix):
        raise ValueError("Name %r must start with prefix %r" %(name, prefix))
    shortName = name[len(prefix):]
    return form.widgets.get(shortName, None)


def extractContentType(form, id):
    """Extract the content type of the widget with the given id."""
    widget = getWidgetById(form, id)
    return zope.contenttype.guess_content_type(widget.filename)[0]


def extractFileName(form, id, cleanup=True, allowEmptyPostfix=False):
    """Extract the filename of the widget with the given id.

    Uploads from win/IE need some cleanup because the filename includes also
    the path. The option ``cleanup=True`` will do this for you. The option
    ``allowEmptyPostfix`` allows to have a filename without extensions. By
    default this option is set to ``False`` and will raise a ``ValueError`` if
    a filename doesn't contain a extension.
    """
    widget = getWidgetById(form, id)
    if not allowEmptyPostfix or cleanup:
        # We need to strip out the path section even if we do not reomve them
        # later, because we just need to check the filename extension.
        cleanFileName = widget.filename.split('\\')[-1]
        cleanFileName = cleanFileName.split('/')[-1]
        dottedParts = cleanFileName.split('.')
    if not allowEmptyPostfix:
        if len(dottedParts) <= 1:
            raise ValueError(_('Missing filename extension.'))
    if cleanup:
        return cleanFileName
    return widget.filename


class UniqueOrderedKeys(object):
    """Ensures that we only use unique keys in a list.

    This is useful since we use the keys and values list only as ordered keys
    and values addition for our data dict.

    Note, this list is only used for Manager keys and not for values since we
    can't really compare values if we will get new instances of widgets or
    actions.
    """

    def __init__(self, values=[]):
        self.data = []
        # ensure that we not intialize a list with duplicated key values
        [self.data.append(value) for value in values]

    def append(self, value):
        if value in self.data:
            raise ValueError(value)
        self.data.append(value)

    def insert(self, position, value):
        if value in self.data:
            raise ValueError(value)
        self.data.insert(position, value)

    #XXX TODO: Inherit from list


class Manager(object):
    """Non-persistent IManager implementation."""
    zope.interface.implements(interfaces.IManager)

    def __init__(self, *args, **kw):
        self.__data_keys = UniqueOrderedKeys()
        self._data_values = []
        self._data = {}

    @apply
    def _data_keys():
        """Use a special ordered list which will check for duplicated keys."""
        def get(self):
            return self.__data_keys
        def set(self, values):
            if isinstance(values, UniqueOrderedKeys):
                self.__data_keys = values
            else:
                self.__data_keys = UniqueOrderedKeys(values)
        return property(get, set)

    def __len__(self):
        return len(self._data_values)

    def __iter__(self):
        return iter(self._data_keys.data)

    def __getitem__(self, name):
        return self._data[name]

    def __delitem__(self, name):
        if name not in self._data_keys.data:
            raise KeyError(name)
        del self._data_keys.data[self._data_keys.data.index(name)]
        value = self._data[name]
        del self._data_values[self._data_values.index(value)]
        del self._data[name]

    def get(self, name, default=None):
        return self._data.get(name, default)

    def keys(self):
        return self._data_keys.data

    def values(self):
        return self._data_values

    def items(self):
        return [(i, self._data[i]) for i in self._data_keys.data]

    def __contains__(self, name):
        return bool(self.get(name))

    #XXX TODO:
    # Add __setitem__ that will add key, value at the end of both lists as in PEP0372
    # Add insertBefore(key)
    #     insertAfter(key)

class SelectionManager(Manager):
    """Non-persisents ISelectionManager implementation."""
    zope.interface.implements(interfaces.ISelectionManager)

    managerInterface = None

    def __add__(self, other):
        if not self.managerInterface.providedBy(other):
            return NotImplemented
        return self.__class__(self, other)

    def select(self, *names):
        """See interfaces.ISelectionManager"""
        return self.__class__(*[self[name] for name in names])

    def omit(self, *names):
        """See interfaces.ISelectionManager"""
        return self.__class__(
            *[item for name, item in self.items()
              if name not in names])

    def copy(self):
        """See interfaces.ISelectionManager"""
        return self.__class__(*self.values())
