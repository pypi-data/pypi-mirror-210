############
Squonk2 Deck
############

.. image:: https://img.shields.io/pypi/pyversions/im-squeck
   :alt: PyPI - Python Version
.. image:: https://img.shields.io/pypi/v/im-squeck
   :alt: PyPI
.. image:: https://img.shields.io/github/license/informaticsmatters/squonk2-deck
   :alt: GitHub
.. image:: https://img.shields.io/github/actions/workflow/status/informaticsmatters/squonk2-deck/build.yaml?label=build%20workflow
   :alt: GitHub Workflow Status
.. image:: https://img.shields.io/github/actions/workflow/status/informaticsmatters/squonk2-deck/publish.yaml?label=publish%20workflow
   :alt: GitHub Workflow Status

**Squeck** (Squonk2 Deck) is s Textual-UI (TUI) for the
summary visualisation of multiple Squonk2 environments.

.. image:: docs/images/screenshot.png

**Squeck** uses the `squonk2-python-client`_ to create a **Deck** displaying
summary information for multiple Squonk2 environments and uses Will McGugan's
`textual`_ framework to provide the user with a simple,
text-based user interface modelled on the popular `k9s`_ Kubernetes monitor.

.. _k9s: https://k9scli.io
.. _squonk2-python-client: https://github.com/InformaticsMatters/squonk2-python-client
.. _textual: https://github.com/Textualize/textual

************
Installation
************

**Squeck** is a Python application, written with Python 3.10 and published
to `PyPI`_ and is easily installed using ``pip``::

    pip install im-squeck

.. _pypi: https://pypi.org/project/im-squeck/

*********
Execution
*********

Before running **Squeck** you must have access to at least one Squonk2 environment.
**Squeck** obtains details of the environment through a YAML-based
*environments* file. An example file, ``environments``, is located in the root
of this project:

When **Squeck** starts it will look for the environments file in your home
directory, in the file ``~/.squonk2/environments``. If you place your populated
environments file there you need do nothing else prior to running **Squeck**.
If you prefer to put your ``environments`` file elsewhere, or have multiple
files, set the path to your file using the environment variable
``SQUONK2_ENVIRONMENTS_FILE``::

    export SQUONK2_ENVIRONMENTS_FILE=~/my-squonk2-environments

With an environments file in place you can run **Squeck**::

    squeck

Logging
-------

You can enable logging from **Squeck** and the underlying textual framework by
setting the environment variable ``SQUONK2_LOGFILE`` when running the
application::

    SQUONK2_LOGFILE=./squeck.log squeck

Debugging
---------

`Textual`_ doesn't like anything being written to the console so printing
(even to ``stderr``) will topple the display. That's why ``stderr`` is
diverted when the application is running and nothing is printed.
There comes a time, though, when you need to see the error log.
For these times you can run **Squeck** without stderr diverted::

    squeck --enable-stderr
