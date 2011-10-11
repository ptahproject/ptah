from memphis import config, view

view.registerLayout(
    'ptah-security', parent='.',
    template = view.template('ptah_crowd:templates/layout.pt'))
