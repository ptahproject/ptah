"""Form implementation"""
import sys
from zope import interface
from zope.component import getAdapters, getMultiAdapter
from zope.lifecycleevent import Attributes, ObjectModifiedEvent

from webob.exc import HTTPFound
from webob.multidict import UnicodeMultiDict, MultiDict

from memphis import view, config
from memphis.form import button, field, interfaces, util, pagelets

_ = interfaces.MessageFactory

empty_params = UnicodeMultiDict(MultiDict({}), 'utf-8')


def applyChanges(form, content, data):
    changes = {}
    for name, field in form.fields.items():
        # If the field is not in the data, then go on to the next one
        if name not in data:
            continue
        # If the value is NOT_CHANGED, ignore it, since the widget/converter
        # sent a strong message not to do so.
        if data[name] is interfaces.NOT_CHANGED:
            continue
        # Get the datamanager and get the original value
        dm = getMultiAdapter((content, field.field), interfaces.IDataManager)
        # Only update the data, if it is different
        # Or we can not get the original value, in which case we can not check
        # Or it is an Object, in case we'll never know
        if dm.query() != data[name]:
            dm.set(data[name])
            # Record the change using information required later
            changes.setdefault(dm.field.interface, []).append(name)
    return changes


def extends(*args, **kwargs):
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    if not kwargs.get('ignoreFields', False):
        f_locals['fields'] = field.Fields()
        for arg in args:
            f_locals['fields'] += getattr(arg, 'fields', field.Fields())
    if not kwargs.get('ignoreButtons', False):
        f_locals['buttons'] = button.Buttons()
        for arg in args:
            f_locals['buttons'] += getattr(arg, 'buttons', button.Buttons())


class Form(view.View):
    """A base form."""
    interface.implements(interfaces.IForm, interfaces.IInputForm)

    fields = field.Fields()
    buttons = button.Buttons()

    label = None
    description = ''

    prefix = 'form.'
    template = None

    actions = None
    widgets  = None

    content = None

    mode = interfaces.INPUT_MODE
    ignoreReadonly = False

    method = 'post'
    enctype = 'multipart/form-data'
    acceptCharset = None
    accept = None
    refreshActions = False

    # common string for use in validation status messages
    formErrorsMessage = _('There were some errors.')

    subforms = ()

    @property
    def action(self):
        try:
            self.request.getURL()
        except:
            return self.request.url

    @property
    def name(self):
        return self.prefix.strip('.')

    @property
    def id(self):
        return self.name.replace('.', '-')

    def getContext(self):
        return self.context

    def getContent(self):
        return self.content

    def getRequestParams(self):
        try:
            return self.request.params
        except:
            return UnicodeMultiDict(self.request.form, 'utf-8')

    def updateWidgets(self):
        self.widgets = getMultiAdapter(
            (self, self.request), interfaces.IWidgets)
        self.widgets.mode = self.mode
        self.widgets.ignoreReadonly = self.ignoreReadonly
        self.widgets.update()

    def updateActions(self):
        self.actions = button.Actions(self, self.request)
        self.actions.update()

    def validate(self, data, errors):
        for name, validator in getAdapters((self,), interfaces.IFormValidator):
            errors.extend(validator.validate(data))

    def extractData(self, setErrors=True):
        self.widgets.setErrors = setErrors
        return self.widgets.extract()

    def update(self):
        self.updateWidgets()
        self.updateActions()

        self.actions.execute()
        if self.refreshActions:
            self.updateActions()

    def render(self):
        # render content template
        if self.template is None:
            return view.renderPagelet(pagelets.IFormView, self, self.request)

        kwargs = {'view': self,
                  'context': self.context,
                  'request': self.request}

        return self.template(**kwargs)


class DisplayForm(Form):
    interface.implements(interfaces.IDisplayForm)

    mode = interfaces.DISPLAY_MODE

    def getRequestParams(self):
        return empty_params


class EditForm(Form):
    """A simple edit form with an apply button."""
    interface.implements(interfaces.IEditForm)

    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')
    formErrorsMessage = _(u'Please fix indicated errors.')

    groups = ()
    subforms = ()

    def extractData(self, setErrors=True):
        data, errors = super(EditForm, self).extractData(setErrors)

        for form in self.groups:
            formData, formErrors = form.extractData(setErrors)
            data.update(formData)
            if formErrors:
                errors += formErrors

        for form in self.subforms:
            formData, formErrors = form.extractData(setErrors)
            if formErrors:
                errors += formErrors

        return data, errors

    def _applyChanges(self, content, data):
        return applyChanges(self, content, data)

    def applyChanges(self, data):
        content = self.getContent()
        changed = self._applyChanges(content, data)

        for form in self.subforms:
            data, errors = form.extractData(setErrors=False)
            for iface, names in form.applyChanges(data).items():
                changed[iface] = changed.get(iface, []) + names

        for group in self.groups:
            data, errors = group.extractData(setErrors=False)
            for iface, names in group.applyChanges(data).items():
                changed[iface] = changed.get(iface, []) + names

        if changed:
            descriptions = []
            for interface, names in changed.items():
                descriptions.append(Attributes(interface, *names))

            # Send out a detailed object-modified event
            config.notify(ObjectModifiedEvent(content, *descriptions))

        return changed

    def listInlineForms(self):
        return [(name, form) for name, form in
                getAdapters((self.context, self.request, self), 
                            interfaces.IInlineForm)]

    def updateForms(self):
        self.groups = []
        self.subforms = []

        for name, form in self.listInlineForms():
            form.__name__ = name
            form.update()
            if not form.isAvailable():
                continue

            if interfaces.IGroup.providedBy(form):
                self.groups.append(form)
            elif interfaces.ISubForm.providedBy(form):
                self.subforms.append(form)

        self.groups.sort(key = lambda f: f.weight)
        self.subforms.sort(key = lambda f: f.weight)

    def update(self):
        self.content = self.context

        self.updateWidgets()
        self.updateActions()
        self.updateForms()

        self.actions.execute()
        if self.refreshActions:
            self.updateActions()

    @button.button(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            view.addMessage(
                self.request, 
                (self.formErrorsMessage,)+tuple(errors), 'formError')
            return

        changed = self.applyChanges(data)
        if changed:
            view.addMessage(self.request, self.successMessage)
        else:
            view.addMessage(self.request, self.noChangesMessage)

        nextURL = self.nextURL()
        if nextURL:
            raise HTTPFound(location=nextURL)

    @button.button(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        data, errors = self.extractData()
        raise HTTPFound(location=self.cancelURL())
    
    def nextURL(self):
        pass

    def cancelURL(self):
        return '../'
