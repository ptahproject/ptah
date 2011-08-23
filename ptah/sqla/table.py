import ptah
import pyramid_sqla
from memphis import view, form

from module import Session
from interfaces import ITable


class TableView(form.Form):
    view.pyramidView(
        'index.html', ITable, route='ptah-manage', default = True,
        template = view.template('ptah.sqla:templates/table.pt'))

    def update(self):
        super(TableView, self).update()

        table = self.table = self.context.table

        self.primary = None
        for cl in table.columns:
            if cl.primary_key:
                self.primary = cl.name

        self.size = Session.query(table).count()
        self.data = Session.query(table).limit(10).all()

    @form.button('Add', actype=form.AC_PRIMARY)
    def add(self):
        pass

    @form.button('Remove', actype=form.AC_DANGER)
    def remove(self):
        pass
