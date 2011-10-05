""" interfaces """
from ptah_cms.interfaces import IContent, IContainer


class IFolder(IContainer):
    """ generic folder """


class IPage(IContent):
    """ page """
