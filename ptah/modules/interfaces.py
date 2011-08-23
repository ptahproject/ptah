import ptah
from zope import interface


class IIntrospectModule(ptah.IPtahModule):
    """ memphis introspection module """


class IPackage(interface.Interface):
    """ """


class ITemplatesModule(ptah.IPtahModule):
    """ templates customization module """
