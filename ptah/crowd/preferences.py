""" preferences form """
from zope import interface
from pyramid import security
from memphis import config, view, form

from models import CrowdUser
from schemas import RegistrationSchema, PasswordSchema
from interfaces import IPreferencesPanel, IPreferencesGroup


class PreferencesPanel(view.DefaultRoot):
    interface.implements(IPreferencesPanel)

    __name__ = 'preferences'
    __parent__ = None


view.registerRoute('ptah-prefs', '/preferences/*traverse',
                   PreferencesPanel, use_global_views=True)


class DefaultView(form.Form):
    view.pyramidView('index.html', IPreferencesPanel, 'ptah-prefs',
                     default=True, layout='ptah-crowd')

    label = 'Preferences'
    fields = form.Fields(RegistrationSchema, PasswordSchema)

    autocomplete = 'off'

    def getContent(self):
        return self.content

    def update(self):
        sm = self.request.registry

        self.fields = fields = form.Fields(RegistrationSchema)

        self.props = props = []
        for name, prop in sm.getUtilitiesFor(IPreferencesGroup):
            props.append(prop)
            fields.append(form.Fieldset(prop.schema))

        id = security.authenticated_userid(self.request)

        user = CrowdUser.get(id)

        self.content = content = form.DataManager(user)

        for prop in self.props:
            content.append(prop.name, prop.get(user.id))

        super(DefaultView, self).update()

    @form.button('Modify', actype=form.AC_PRIMARY)
    def modifyHandler(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        print data
