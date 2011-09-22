import colander
from memphis import config, view

view.registerLayout(
    'ptah-security', parent='.',
    template = view.template('ptah.crowd:templates/layout.pt'))
