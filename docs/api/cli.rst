dwind.cli
=========

Please see the [CLI documentation](../cli) for more details on using the CLI. Below is a summary
of the available functionality best accessed through the CLI.

.. automodule:: dwind.cli


.. rubric:: Modules

.. autosummary::

   run
   debug
   collect
   utils

Run
---

.. automodule:: dwind.cli.run
    :members:

    .. rubric:: Functions

    .. autosummary::
      chunk
      config
      hpc
      interactive

Debug
-----

.. automodule:: dwind.cli.debug
    :members:

    .. rubric:: Functions

    .. autosummary::
      job_summary
      missing_agents
      missing_agents_from_chunks

Collect
-------

.. automodule:: dwind.cli.collect
    :members:

    .. rubric:: Functions

    .. autosummary::
      cleanup_agents
      cleanup_results
      combine_chunks

Utilities
---------

.. automodule:: dwind.cli.utils
    :members:

    .. rubric:: Functions

    .. autosummary::
      cleanup_chunks
      load_agents
      print_status_table
      year_callback
