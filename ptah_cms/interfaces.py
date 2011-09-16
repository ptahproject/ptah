""" interfaces """
import colander
from zope import interface


class INode(interface.Interface):
    """ base """

    __id__ = interface.Attribute('Id')
    __uuid__ = interface.Attribute('UUID')
    __type_id__ = interface.Attribute('Node type')
    __parent_id__ = interface.Attribute('Node parent')


class IContent(interface.Interface):
    """ base interface """

    name = interface.Attribute('Name')


class IContainer(IContent):
    """ base container content """

    __path__ = interface.Attribute('traversal path')

    
class IApplicationRoot(IContent, IContainer):
    """ application root object """


class IAction(interface.Interface):

    id = interface.Attribute('Id')
    title = interface.Attribute('Title')
    description = interface.Attribute('Description')
    permission = interface.Attribute('Permission')
    action = interface.Attribute('Action')


class ITypeInformation(interface.Interface):
    """ Content type information """


class IRestAction(interface.Interface):
    """ action """

    def __init__(self, content, request):
        """ execute action, return dictionary """


class IRestActionClassifier(interface.Interface):
    """ rest action """


class IBlob(INode):
    """ blob """

    mimetype = interface.Attribute('Blob mimetype')
    filename = interface.Attribute('Original filename')
    data = interface.Attribute('Blob data')


class IBlobStorage(interface.Interface):
    """ blob storage """

    def add(parent, data, mimetype=None, filename=None):
        """ add blob return uuid """

    def query(uuid):
        """ return blob object """

    def replace(uuid, data, mimetype=None, filename=None):
        """ replace existing blob """

    def remove(uuid):
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
