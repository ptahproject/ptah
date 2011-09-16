""" Application policy """
import ptah
from memphis import view
from zope import interface


class ApplicationPolicy(object):
    interface.implements(view.INavigationRoot)

    __name__ = ''
    __parent__ = None

    # default acl
    __acl__ = ptah.security.ACL

    def __init__(self, request):
        self.request = request
