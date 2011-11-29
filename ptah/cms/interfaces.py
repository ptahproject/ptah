""" interfaces """
from zope import interface
from ptah import form
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


class IApplicationRoot(interface.Interface):
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

    def is_allowed(container):
        """ allow create this content in container """

    def check_context(container):
        """ same as isAllowed, but raises HTTPForbidden """

    def list_types(self, container):
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


ContentSchema = form.Fieldset(

    form.FieldFactory(
        'text',
        'title',
        title = 'Title'),

    form.FieldFactory(
        'textarea',
        'description',
        title = 'Description',
        missing = ''),
    )


def specialSymbols(field, appstruct):
    if '/' in appstruct:
        raise form.Invalid(field, "Names cannot contain '/'")
    if appstruct.startswith(' '):
        raise form.Invalid(field, "Names cannot starts with ' '")


ContentNameSchema = form.Fieldset(

    form.FieldFactory(
        'text',
        '__name__',
        title = 'Short Name',
        description = 'Short name is the part that shows up in '\
                            'the URL of the item.',
        missing = '',
        validator = specialSymbols)
    )
