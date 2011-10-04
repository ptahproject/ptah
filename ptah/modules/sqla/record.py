from memphis import view, form
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

from module import Session
from fields import buildSchema
from interfaces import IRecord, ITable


class EditRecord(form.Form):
    view.pyramidView(context = IRecord)

    __doc__ = "Edit table record."
    __intr_path__ = '/ptah-manage/sqla/${table}/${record}/index.html'

    csrf = True

    @reify
    def label(self):
        return '%s: record %s'%(self.context.table.name, self.context.__name__)

    @reify
    def fields(self):
        return form.Fieldset(buildSchema(self.context.table))

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
        self.validateToken()

        self.context.table.delete(
            self.context.pcolumn == self.context.__name__).execute()
        self.message('Table record has been removed.')
        raise HTTPFound(location='../')


class AddRecord(form.Form):
    """ Add new table record. """
    view.pyramidView('add.html', ITable)

    __intr_path__ = '/ptah-manage/sqla/${table}/add.html'

    csrf = True

    @reify
    def label(self):
        return '%s: new record'%self.context.table.name

    @reify
    def fields(self):
        return form.Fieldset(buildSchema(self.context.table))

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
