""" This is an example of security and URI resolver in 1 module. """
import ptah
from ptah import view
from paste.httpserver import serve

# this is login, bobdobbs whose prefix is user-example.
# the default Ptah implementation is ptah.crowd.provider, scheme `user-crowd`

USERS = {'user-example:bobdobbs':'aliens'}
SCHEME = 'user-example'

class User(object):

    def __init__(self, login):
        self.uri = '%s:%s' % (SCHEME, login)
        self.password = USERS.get(self.uri)
        self.login = login
        self.name = login

    @classmethod
    def get(cls, login):
        login = login.split(':',1)[-1]

        if USERS.get('%s:%s' % (SCHEME, login)):
            return User(login)

    get_bylogin = get_byuri = get


class UserProvider(object):

    def authenticate(self, creds):
        login, password = creds['login'], creds['password']
        user = User.get(login)
        if user is not None:
            return user

    def get_principal_bylogin(self, login):
        return User(login)


# registration
@ptah.resolver('user-example', 'An example principal resolver')
def getPrincipal(uri):
    return User.get(uri)

ptah.register_auth_provider('example', UserProvider())


if __name__ == '__main__':
    """ need to point to your settings.ini file in make_wsgi_app call.
        http://localhost:8080/show_models is url dispatch function.
        http://localhost:8080/list_children is traverser on context
        $resource_url/show_info on either folder or content.
    """
    from pyramid.config import Configurator

    config = Configurator(settings={'settings':r'./ptah.ini'})
    config.include('ptah')
    config.ptah_init()
    app = config.make_wsgi_app()

    serve(app, host='0.0.0.0')
