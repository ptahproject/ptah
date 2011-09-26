import ptah
import sqlalchemy as sqla
import pyramid_sqla as psa
from zope import interface

from interfaces import IPrincipalWithEmail

Base = psa.get_base()
Session = psa.get_session()


class CrowdProvider(object):
    interface.implements(ptah.IAuthProvider)

    def authenticate(self, creds):
        login, password = creds['login'], creds['password']

        user = CrowdUser.getByLogin(login)

        if user is not None:
            if ptah.passwordTool.checkPassword(user.password,password):
                return user

    def getPrincipalByLogin(self, login):
        return CrowdUser.getByLogin(login)


UUID = ptah.UriGenerator('user+crowd')


class CrowdUser(Base):
    interface.implements(IPrincipalWithEmail)

    __tablename__ = 'ptah_crowd'

    pid = sqla.Column(sqla.Integer, primary_key=True)
    uuid = sqla.Column(sqla.Unicode(45), unique=True)
    name = sqla.Column(sqla.Unicode(255))
    login = sqla.Column(sqla.Unicode(255), unique=True)
    email = sqla.Column(sqla.Unicode(255), unique=True)
    password = sqla.Column(sqla.Unicode(255))

    def __init__(self, name, login, email, password=u''):
        super(Base, self).__init__()

        self.name = name
        self.uuid = UUID()
        self.login = login
        self.email = email
        self.password = password

    _sql_get = ptah.QueryFreezer(
        lambda: Session.query(CrowdUser)\
           .filter(CrowdUser.uuid==sqla.sql.bindparam('uuid')))

    _sql_get_pid = ptah.QueryFreezer(
        lambda: Session.query(CrowdUser)\
           .filter(CrowdUser.pid==sqla.sql.bindparam('pid')))

    _sql_get_login = ptah.QueryFreezer(
        lambda: Session.query(CrowdUser)\
           .filter(CrowdUser.login==sqla.sql.bindparam('login')))

    @classmethod
    def get(cls, id):
        return cls._sql_get.first(uuid=id)

    @classmethod
    def getById(cls, id):
        return cls._sql_get_pid.first(pid=id)

    @classmethod
    def getByLogin(cls, login):
        return cls._sql_get_login.first(login=login)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s <%s>'%(self.name, self.uuid)


def changeCrowdUserPassword(principal, password):
    principal.password = password


def getPrincipal(uuid):
    return CrowdUser.get(uuid)


_sql_search = ptah.QueryFreezer(
    lambda: Session.query(CrowdUser) \
    .filter(
        sqla.sql.or_(CrowdUser.email.contains(sqla.sql.bindparam('term')),
                     CrowdUser.name.contains(sqla.sql.bindparam('term'))))\
    .order_by(sqla.sql.asc('name')))

def searchPrincipals(term):
    for user in _sql_search.all(term = '%%%s%%'%term):
        yield user


ptah.registerResolver('user+crowd', getPrincipal)
ptah.registerProvider('crowd', CrowdProvider())
ptah.registerSearcher('crowd', searchPrincipals)
ptah.passwordTool.registerPasswordChanger('user+crowd', changeCrowdUserPassword)
