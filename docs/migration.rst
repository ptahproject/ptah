.. _data_migration_chapter:

Data migration
==============

Ptah migration based on `alembic <http://readthedocs.org/docs/alembic/>`_ package.
Ptah adds per package migration. Migration is not required `alembic` 
environment. 


Create package migration
~~~~~~~~~~~~~~~~~~~~~~~~

You can use `alembic operations <http://readthedocs.org/docs/alembic/en/latest/ops.html>`_ for ddl manipulation. Here are the steps for ptah migrations 
generation.

* Create directory in your package that will contain migration steps. 

 For example:

 .. code-block:: text
   :linenos:

   $ cd ptah_minicms
   $ mkdir migrations


 So directory listing should look like this:

 .. code-block:: text
   :linenos:

   $ ls -l
   drwxrwxr-x 2 fafhrd fafhrd 4096 2012-01-11 15:58 migrations
   drwxrwxr-x 2 fafhrd fafhrd 4096 2011-12-16 11:33 static
   drwxrwxr-x 2 fafhrd fafhrd 4096 2011-12-29 14:50 templates
   -rw-rw-r-- 1 fafhrd fafhrd 1457 2011-12-29 14:50 actions.py
   ...

* Register package migrations with :py:func:`ptah.register_migration` api.

 .. code-block:: python
   :linenos:

   import ptah

   ptah.register_migration(
       'ptah_minicms', 'ptah_minicms:migrations',
       'Ptah minicms example migration')

 First parameter is package name, second parameter is `asset` style path and
 third parameter migration title.

* To create new revision you should use ``ptah-migrate`` script.

 .. code-block:: text
   :linenos:

   $ /bin/ptah-migrate settings.ini revision ptah_minicms -r 001 -m "Add column"
   Generating /path-to-virtualenv/ptah_minicms/migrations/001.py...done

 Generated script contains empty ``update()`` and ``downgrade()`` function.
 Add code that does migration from previous revision to this function.

* Now you can use ``ptah-migrate`` script to execute migration steps.

 .. code-block:: text
   :linenos:

   $ bin/ptah-migrate settings.ini upgrade ptah_minicms
   2012-01-11 16:14:42,657 INFO  [ptah.alembic] ptah_minicms: running upgrade None -> 001

Check :ref:`data_migration_script` chapter for ``ptah-migrate`` script detailed description.


Migration data during start up
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use :ref:`ptah_migrate_dir` pyramid directive for migration data schema
during startup.


.. code-block:: python

  import ptah
  from pyramid.config import Configurator

  def main(global_settings, **settings):
  
      config = Configurator(settings=settings)
      config.include('ptah')

      ...

      config.ptah_migrate()

      ...

      return config.make_wsgi_app()

Migration steps are executed after configration commited.


Notes
~~~~~

* Ptah stores package revision numbers in ``ptah_db_versions`` table. During
  data population process `ptah` checks if ``ptah_db_versions`` table contains
  version info, if it doesnt contain version information ``ptah`` just set 
  latest revision without running migration steps. It assumes if there is no 
  version information then database schema is latest.

* ``ptah-migrate`` script calls populate subsystem before running any upgrade
  steps.
