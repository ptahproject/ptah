Data population
===============

Data population process consists of populate steps. Each step can be marked
as active or inactive. Active steps are executed by ``ptah_populate`` 
pyramid directive and ``ptah-populate -a `` command-line script.
also it is possible to specify ``requires`` for each step. ``requires`` 
is a list of steps that should be executed before step.


Define step
~~~~~~~~~~~

Interface of populate step is very simple. It is function that accepts
one argument pyramid ``registry`` :py:class:`ptah.interfaces.populate_step`.

.. code-block:: python

  import ptah

  @ptah.populate('custom-populate-step')
  def populate_step(registry):
      ...


Check :py:class:`ptah.populate` for detailed description of this directive.


Populate data during start up
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use :ref:`ptah_populate_dir` pyramid directive for populate system data
during startup.


.. code-block:: python

  import ptah
  from pyramid.config import Configurator

  def main(global_settings, **settings):
  
      config = Configurator(settings=settings)
      config.include('ptah')

      ...

      config.ptah_populate()

      ...

      return config.make_wsgi_app()

Populate steps are executed after configration commited.


Command line script
~~~~~~~~~~~~~~~~~~~

Ptah providers ``ptah-populate`` command-line script for data population.

.. code-block:: text
   
   [fafhrd@... MyProject]$ ../bin/ptah-populate development.ini -a
   ...


Check :ref:`data_populate_script` for detailed description of this script.
