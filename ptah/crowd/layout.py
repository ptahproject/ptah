from memphis import view
from interfaces import ICrowdUser, ICrowdModule, IManageUserAction


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
        actions = []
        if ICrowdUser.providedBy(self.view.context):
            registry = self.request.registry
            url = self.request.route_url('ptah-manage', traverse='crowd/')
            self.url = '%s%s/'%(url, self.view.context.__name__)
            self.user = self.view.context.user.name
            for name, util in registry.getUtilitiesFor(IManageUserAction):
                if util.available(self.view.context.user):
                    actions.append((util.title, util))

        actions.sort()
        self.actions = [a for t, a in actions]
