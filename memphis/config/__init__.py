# memphis.config package public API

from memphis.config.api import begin
from memphis.config.api import commit

from memphis.config.api import UNSET
from memphis.config.api import getContext
from memphis.config.api import addPackage
from memphis.config.api import loadPackage
from memphis.config.api import loadPackages
from memphis.config.api import action as addAction
from memphis.config.api import cleanup
from memphis.config.api import registerCleanup
from memphis.config.api import moduleNum

from memphis.config.api import registerAdapter
from memphis.config.api import registerUtility
from memphis.config.api import registerHandler

from memphis.config.zca import registry
from memphis.config.zca import getRegistry

from memphis.config.directives import getInfo
from memphis.config.directives import adapts
from memphis.config.directives import adapter
from memphis.config.directives import handler
from memphis.config.directives import action
from memphis.config.directives import utility
from memphis.config.directives import registerIn

from memphis.config.settings import Settings
from memphis.config.settings import FileStorage
from memphis.config.settings import SimpleWatcher
from memphis.config.settings import initSettings
from memphis.config.settings import registerSettings


commitOnDatabaseOpened = True
try:
    from zope.processlifetime import IDatabaseOpenedWithRoot

    import pkg_resources
    from zope.component import getSiteManager

    def commitConfig(ev):
        if commitOnDatabaseOpened:
            for dist in pkg_resources.working_set:
                distmap = pkg_resources.get_entry_map(dist, 'memphis')
                if distmap:
                    loadPackage(dist.project_name)

            begin()
            commit()

    getSiteManager().registerHandler(commitConfig, (IDatabaseOpenedWithRoot,))

except ImportError:
    pass
