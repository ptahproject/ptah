from memphis import view
from interfaces import ICrowdUser, ICrowdModule, IManageUserAction, IManageAction


view.registerLayout(
    'ptah-crowd', parent='.',
    template = view.template('ptah.crowd:templates/layout.pt'))


class LayoutMain(view.Layout):
    view.layout(
        '', ICrowdModule, parent='page',
        template = view.template('ptah.crowd:templates/layout-manage.pt'))

    actions = ()
    user = None

    def update(self):
        registry = self.request.registry
        self.url = self.request.route_url('ptah-manage', traverse='')

        actions = []

        if ICrowdModule.providedBy(self.view.context):
            for name, util in registry.getUtilitiesFor(IManageAction):
                if util.available():
                    actions.append((util.title, util))

        elif ICrowdUser.providedBy(self.view.context):
            self.url = '%s%s/'%(self.url, self.view.context.__name__)
            self.user = self.view.context.user.name
            for name, util in registry.getUtilitiesFor(IManageUserAction):
                if util.available(self.view.context.user):
                    actions.append((util.title, util))

        actions.sort()
        self.actions = [a for t, a in actions]
