""" interfaces """
import colander
from zope import interface
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden, HTTPServerError


class CmsException(Exception):
    """ """

class Forbidden(HTTPForbidden, CmsException):
    """ something forbidden """


class NotFound(HTTPNotFound, CmsException):
    """ something not found """


class Error(HTTPServerError, CmsException):
    """ internale error """


class INode(interface.Interface):
    """ base """

    __id__ = interface.Attribute('Id')
    __uri__ = interface.Attribute('Uri')
    __type_id__ = interface.Attribute('Node type')
    __parent_uri__ = interface.Attribute('Node parent')


class IContent(interface.Interface):
    """ base interface """

    name = interface.Attribute('Name')


class IContainer(IContent):
    """ base container content """

    __path__ = interface.Attribute('traversal path')


class IApplicationPolicy(interface.Interface):
    """ application policy """


class IApplicationRoot(IContent, IContainer):
    """ application root object """

    __root_path__ = interface.Attribute('Current mount point')


class IApplicationRootFactory(interface.Interface):
    """ application root factory """

    def __call__(**kw):
        """ return ApplicationRoot object """


class ITypeInformation(interface.Interface):
    """ Content type information """

    name = interface.Attribute('Name')
    title = interface.Attribute('Title')
    description = interface.Attribute('Description')

    permission = interface.Attribute('Add permission')

    filter_content_types = interface.Attribute('Filter addable types')
    allowed_content_types = interface.Attribute('List of addable types')
    global_allow = interface.Attribute('Addable globally')

    def create(**data):
        """ construct new content instance """

    def isAllowed(container):
        """ allow create this content in container """

    def checkContext(container):
        """ same as isAllowed, but raises HTTPForbidden """

    def listTypes(self, container):
        """ list addable content types """


class IBlob(INode):
    """ blob """

    mimetype = interface.Attribute('Blob mimetype')
    filename = interface.Attribute('Original filename')
    data = interface.Attribute('Blob data')


class IBlobStorage(interface.Interface):
    """ blob storage """

    def add(parent, data, mimetype=None, filename=None):
        """ add blob return uri """

    def query(uri):
        """ return blob object """

    def replace(uri, data, mimetype=None, filename=None):
        """ replace existing blob """

    def remove(uri):
        """ remove blob """


class ContentSchema(colander.Schema):
    """ base content schema """

    title = colander.SchemaNode(
        colander.Str(),
        title = 'Title')

    description = colander.SchemaNode(
        colander.Str(),
        title = 'Description',
        missing = u'',
        widget = 'textarea')


def specialSymbols(node, appstruct):
    if '/' in appstruct:
        raise colander.Invalid(node, "Names cannot contain '/'")
    if appstruct.startswith(' '):
        raise colander.Invalid(node, "Names cannot starts with ' '")


class ContentNameSchema(colander.Schema):
    """ name schema """

    __name__ = colander.SchemaNode(
        colander.Str(),
        title = 'Short Name',
        description = 'Short name is the part that shows up in '\
                            'the URL of the item.',
        missing = u'',
        validator = specialSymbols)
