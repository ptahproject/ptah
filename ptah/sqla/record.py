from webob.exc import HTTPFound
from memphis import view, form
from pyramid.decorator import reify

from module import Session
from fields import buildSchema
from interfaces import IRecord


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

    @form.button('Modify and return', actype=form.AC_PRIMARY)
    def save(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        self.context.table.update(
            self.context.pcolumn == self.context.__name__, data).execute()
        self.message('Table record has been modified.', 'success')
        raise HTTPFound(location='../')
