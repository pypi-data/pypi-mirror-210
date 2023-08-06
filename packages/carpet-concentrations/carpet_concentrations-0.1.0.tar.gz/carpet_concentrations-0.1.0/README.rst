.. sec-begin-description

Carpet - Concentrations
=======================

[TODO badges here #1]

Core tools for the development of greenhouse gas concentration input files (i.e.
flying carpets).

Full documentation can be found at: [TODO read the docs link here #2]

.. sec-begin-links

.. _issue tracker: https://gitlab.com/climate-resource/carpet-concentrations/-/issues

.. sec-end-links

.. sec-end-description

Installation
------------

Carpet - concentrations can be installed with conda or pip:

.. code:: bash

    pip install carpet-concentrations
    conda install -c conda-forge carpet-concentrations

Additional dependencies can be installed using

.. code:: bash

    # To add plotting dependencies
    pip install carpet-concentrations[plots]
    # To run the notebooks
    pip install carpet-concentrations[notebooks, plots]
    # If you are installing with conda, we recommend
    # installing the extras by hand because there is no stable
    # solution yet (issue here: https://github.com/conda/conda/issues/7502)

.. sec-end-installation

.. sec-begin-installation-dev

For developers
~~~~~~~~~~~~~~

For development, we rely on `poetry <https://python-poetry.org>`_ for all our
dependency management. To get started, you will need to make sure that poetry
is installed
(https://python-poetry.org/docs/#installing-with-the-official-installer, we
found that pipx and pip worked better to install on a Mac).

For all of work, we use our ``Makefile``.
You can read the instructions out and run the commands by hand if you wish,
but we generally discourage this because it can be error prone and doesn't
update if dependencies change (e.g. the environment is updated).
In order to create your environment, run ``make virtual-environment``.

If there are any issues, the messages from the ``Makefile`` should guide you
through. If not, please raise an issue in the
`issue tracker`_.

.. sec-end-installation-dev
