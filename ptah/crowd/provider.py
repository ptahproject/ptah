from zope import interface
from sqlalchemy import sql

import ptah
from ptah.crowd.models import Session, CrowdUser


class CrowdProvider(object):
    interface.implements(ptah.security.IAuthProvider,
                         ptah.security.ISearchableAuthProvider)

    def authenticate(self, creds):
        login, password = creds['login'], creds['password']

        user = CrowdUser.getByLogin(login)

        if user is not None:
            if ptah.security.passwordTool.checkPassword(user.password, password):
                return user.uuid, user.name, login

    def getPrincipalInfo(self, id):
        user = CrowdUser.get(id)
        if user is not None:
            return user.name, user.login

    def getPrincipalInfoByLogin(self, login):
        user = CrowdUser.getByLogin(login)
        if user is not None:
            return user.uuid, user.name, user.login

    def search(self, term):
        for user in Session.query(CrowdUser) \
            .filter(sql.or_(CrowdUser.email.contains('%%%s%%'%term),
                            CrowdUser.name.contains('%%%s%%'%term)))\
            .order_by(sql.asc('name')).all():
            yield user.uuid, user.name, user.login


ptah.security.registerProvider('crowd', CrowdProvider())
