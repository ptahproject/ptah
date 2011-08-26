import ptah
import pyramid_sqla
from memphis import view

from interfaces import ITable

Session = pyramid_sqla.get_session()


class TableView(view.View):
    view.pyramidView(
        'index.html', ITable, route='ptah-manage', default = True,
        template = view.template('ptah.sqla:templates/table.pt'))

    def update(self):
        table = self.table = self.context.table

        self.size = Session.query(table).count()
        self.data = Session.query(table).limit(10).all()
