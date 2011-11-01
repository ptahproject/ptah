from ptah import manage, view

class MyModule(manage.PtahModule):
    """
    REST Introspector
    """
    title = 'REST Introspector'
    manage.module('myapp2')

class MyModuleView(view.View):
    view.pview(
        context = MyModule,
        template = view.template('ptah.manage:templates/rest.pt'))

    def update(self):
        self.appurl = self.request.application_url
        self.url = self.request.get('url', '%s/__rest__/cms/' % self.appurl)
