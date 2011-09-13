""" default content forms """
from memphis import view, form
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

from interfaces import IContent
from permissions import ModifyContent


class EditForm(form.Form):
    view.pyramidView('edit.html', IContent,  permission=ModifyContent)

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
