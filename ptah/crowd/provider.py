import ptah
import sqlalchemy as sqla
import pyramid_sqla as psa
from zope import interface

Base = psa.get_base()
Session = psa.get_session()


class CrowdProvider(object):
    interface.implements(ptah.security.IAuthProvider)

    def authenticate(self, creds):
        login, password = creds['login'], creds['password']

        user = CrowdUser.getByLogin(login)

        if user is not None:
            if ptah.security.passwordTool.checkPassword(user.password,password):
                return user

    def getPrincipal(self, uuid):
        return CrowdUser.get(uuid)

    def getPrincipalInfoByLogin(self, login):
        return CrowdUser.getByLogin(login)

    _sql_search = ptah.QueryFreezer(
        lambda: Session.query(CrowdUser) \
        .filter(
            sqla.sql.or_(CrowdUser.email.contains(sqla.sql.bindparam('term')),
                         CrowdUser.name.contains(sqla.sql.bindparam('term'))))\
        .order_by(sqla.sql.asc('name')))

    def search(self, term):
        for user in self._sql_search.all(term = '%%%s%%'%term):
            yield user


provider = CrowdProvider()
ptah.registerResolver('user+crowd', provider.getPrincipal)
ptah.security.registerProvider('crowd', provider)
ptah.security.registerSearcher('crowd', provider.search)

UUID = ptah.UUIDGenerator('user+crowd')


class CrowdUser(Base):
    interface.implements(ptah.security.IPrincipalWithEmail,
                         ptah.security.IPasswordChanger)

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
    principal.password = ptah.security.passwordTool.encodePassword(password)

ptah.security.passwordTool.registerPasswordChanger(
    'user+crowd', changeCrowdUserPassword)
