"""Utilities helpful to the package."""
import re, string
from collections import OrderedDict
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


class OrderedDict(OrderedDict):

    def __add__(self, other):
        return self.__class__(self, other)
