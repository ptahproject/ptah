from webob.exc import HTTPFound
from memphis import view, form
from pyramid.decorator import reify

from module import Session
from fields import buildSchema
from interfaces import IRecord, ITable


class EditRecord(form.Form):
    view.pyramidView(
        'index.html', IRecord, 'ptah-manage', default = True)

    @reify
    def label(self):
        return '%s: record %s'%(self.context.table.name, self.context.__name__)

    @reify
    def fields(self):
        return form.Fields(buildSchema(self.context.table))

    def getContent(self):
        return self.context.data

    @form.button('Cancel')
    def modify(self):
        raise HTTPFound(location='../')

    @form.button('Modify', actype=form.AC_PRIMARY)
    def modify(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        self.context.table.update(
            self.context.pcolumn == self.context.__name__, data).execute()
        self.message('Table record has been modified.', 'success')
        raise HTTPFound(location='../')

    @form.button('Remove', actype=form.AC_DANGER)
    def remove(self):
        self.context.table.delete(
            self.context.pcolumn == self.context.__name__).execute()
        self.message('Table record has been removed.')
        raise HTTPFound(location='../')


class AddRecord(form.Form):
    view.pyramidView('add.html', ITable, 'ptah-manage')

    @reify
    def label(self):
        return '%s: new record'%self.context.table.name

    @reify
    def fields(self):
        return form.Fields(buildSchema(self.context.table))

    @form.button('Create', actype=form.AC_PRIMARY)
    def create(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        try:
            self.context.table.insert(values = data).execute()
        except Exception, e:
            self.message(e, 'error')
            return

        self.message('Table record has been created.', 'success')
        raise HTTPFound(location='./')

    @form.button('Save & Create new', actype=form.AC_PRIMARY)
    def create_multiple(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        try:
            self.context.table.insert(values = data).execute()
        except Exception, e:
            self.message(e, 'error')
            return

        self.message('Table record has been created.', 'success')

    @form.button('Back')
    def cancel(self):
        raise HTTPFound(location='./')
