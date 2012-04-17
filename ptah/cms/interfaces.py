""" interfaces """
from zope import interface
from pyramid.httpexceptions import HTTPServerError

from ptah import form
from ptah.interfaces import TypeException, Forbidden, NotFound


class Error(HTTPServerError, TypeException):
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
