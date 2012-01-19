# ptah manage api

from ptah.manage.manage import module
from ptah.manage.manage import get_manage_url

from ptah.manage.manage import PtahModule
from ptah.manage.manage import PtahManageRoute

from ptah.manage.manage import check_access
from ptah.manage.manage import set_access_manager
from ptah.manage.manage import PtahAccessManager

from ptah.manage.manage import MANAGE_ACTIONS

from ptah.manage.apps import MANAGE_APP_ROUTE
from ptah.manage.apps import MANAGE_APP_CATEGORY


# pyramid include
def includeme(config):
    config.add_route(
        MANAGE_APP_ROUTE, '# {0}'.format(MANAGE_APP_ROUTE),
        use_global_views=False)
