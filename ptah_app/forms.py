""" default content forms """
import colander
from memphis import view, form
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

from ptah_cms.interfaces import IContent
from ptah_cms.permissions import ModifyContent


def specialSymbols(node, appstruct):
    if '/' in appstruct:
        raise colander.Invalid(node, "Names cannot contain '/'")


class NameSchema(colander.Schema):
    """ name schema """

    __name__ = colander.SchemaNode(
        colander.Str(),
        title = 'Short Name',
        description = 'Short name is the part that shows up in '\
                            'the URL of the item.',
        validator = specialSymbols)


class AddForm(form.Form):

    name_fields = form.Fields(NameSchema)

    @reify
    def label(self):
        return 'Add %s'%self.tinfo.title

    @reify
    def description(self):
        return self.tinfo.description

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()
        
        self.name_widgets = \
            form.FieldWidgets(self.name_fields, self, self.request)
        self.name_widgets.mode = self.mode
        self.name_widgets.update()

    def validate(self, data, errors):
        super(AddForm, self).validate(data, errors)

        if '__name__' in data:
            widget = self.name_widgets['__name__']
            
            name = data['__name__']
            if name in self.context.keys():
                error = colander.Invalid(
                    self.name_fields['__name__'].node, 'Name already in user')
                errors.append(error)

    def extractData(self, setErrors=True):
        data, errors = self.widgets.extract(setErrors)

        name_data, name_errors = self.name_widgets.extract(setErrors)
        if name_errors:
            errors.extend(name_errors)

        data.update(name_data)
        return data, errors

    def update(self):
        self.tinfo = self.context.__type__

        super(AddForm, self).update()


view.registerPagelet(
    'form-actions', AddForm,
    template = view.template('ptah_app:templates/form-actions.pt'))


class EditForm(form.Form):
    view.pyramidView('edit.html', IContent, permission=ModifyContent)

    @reify
    def label(self):
        return 'Modify content: %s'%self.tinfo.title

    @reify
    def fields(self):
        return form.Fields(self.tinfo.schema)

    def getContent(self):
        return self.context

    def update(self):
        self.tinfo = self.context.__type__

        super(EditForm, self).update()

    @form.button('Save', actype=form.AC_PRIMARY)
    def saveHandler(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        for attr, value in data.items():
            setattr(self.context, attr, value)

        self.message("Changes have been saved.")
        raise HTTPFound(location='.')

    @form.button('Cancel')
    def cancelHandler(self):
        raise HTTPFound(location='.')
