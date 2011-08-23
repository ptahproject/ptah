""" add/edit user """
from zope import interface
from webob.exc import HTTPFound
from memphis import config, view, form

from models import User, Session
from schemas import UserSchema, ManagerChangePasswordSchema
from interfaces import _, IPasswordTool, ICrowdUser, IManageUserAction


class CreateUserForm(form.Form):
    view.pyramidView('create-user.html', route='ptah-manage')

    label = _('Create new user')
    fields = form.Fields(UserSchema).omit('id', 'joined')

    @form.button(_('Create'), actype=form.AC_PRIMARY)
    def create(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        # create user
        user = User(data['fullname'], data['login'], data['login'])
        
        if not data['validate']:
            user.validated = True

        if data['suspend']:
            user.suspended = True

        # set password
        passwordtool = self.request.registry.getUtility(IPasswordTool)
        user.password = passwordtool.encodePassword(data['password'])
        Session.add(user)
        Session.flush()

        self.message('User has been created.', 'success')
        raise HTTPFound(location='./')

        #event.notify(ObjectCreatedEvent(item))


class Info(object):
    config.utility(name='user-info')
    interface.implements(IManageUserAction)

    title = _('Information')
    action = 'index.html'

    def available(self, principal):
        return True


class UserInfo(form.Form):
    view.pyramidView('index.html', ICrowdUser,
                     route = 'ptah-manage', default = True)

    label = 'Create user'

    fields = form.Fields(UserSchema)
    fields['id'].readonly = True
    fields['joined'].readonly = True

    def getContent(self):
        return self.context.user
    
    @form.button(_('Activate'),)
    def activate(self):
        #user.suspended = False
        #self.message("Account has been activated.", 'info')
        pass

    @form.button(_('Suspend'),)
    def suspend(self):
        #    user.suspended = True
        #    self.message("Account has been suspended.", 'info')
        pass

    @form.button(_('Validate'),)
    def validate(self):
        #user.validated = True
        #self.message("Account  has been validated.", 'info')
        pass

    @form.button(_('Remove'),)
    def remove(self):
        #<input type="submit" class="btn danger" value="Remove" />
        #user.validated = True
        #self.message("Account  has been validated.", 'info')
        pass


class ChangePasswordAction(object):
    config.utility(name='user-password')
    interface.implements(IManageUserAction)

    title = _('Change password')
    action = 'change-password.html'

    def available(self, principal):
        return True


class ChangePassword(form.Form):
    view.pyramidView('change-password.html', ICrowdUser, route = 'ptah-manage')

    fields = form.Fields(ManagerChangePasswordSchema)

    label = _('Change password')
    description = _('Please specify password for this users.')
    
    @form.button(_('Change'), actype=form.AC_PRIMARY)
    def change(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        self.context.user.password = \
            getUtility(IPasswordTool).encodePassword(data['password'])

        self.message("User password has been changed.")
