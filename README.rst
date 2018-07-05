dev-pipeline-configure
======================
|codacy|
|code-climate|

A `dev-pipeline`_ plugin to provide the :code:`configure` command.
:code:`configure` is used to prepare a project for use, and is required before
any other command will work.


Installation
------------
The simplest way to install is using pip_.

.. code:: bash

    $ cd /path/to/dev-pipeline-configure
    $ pip3 install

If you don't have pip available, you can run :code:`setup.py` directly.

.. code:: bash

    $ cd /path/to/dev-pipeline-configure
    $ python3 setup.py install


Documentation
-------------
Information about the :code:`configure` command is avaialble in the
documentation_.


.. |codacy| image:: https://api.codacy.com/project/badge/Grade/381a33b4d5024790acc0896057dabf7f
    :target: https://www.codacy.com/app/snewell/dev-pipeline-configure?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dev-pipeline/dev-pipeline-configure&amp;utm_campaign=Badge_Grade

.. |code-climate| image:: https://api.codeclimate.com/v1/badges/a12183571a4a37ee887b/maintainability
   :target: https://codeclimate.com/github/dev-pipeline/dev-pipeline-configure/maintainability
   :alt: Maintainability

.. _dev-pipeline: https://github.com/dev-pipeline/dev-pipeline
.. _documentation: docs/command-configure.rst
.. _pip: https://pypi.python.org/pypi/pip
