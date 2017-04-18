[![Build Status](https://travis-ci.org/lukassup/route-ctl.svg?branch=master)](https://travis-ci.org/lukassup/route-ctl)

route-cli
=========

``route-cli`` is a Python CLI Puppet routes resource manager.

.. _installation:

Installation
------------

Supported versions of Python are: 2.6, 2.7, 3.3, 3.4, 3.5 and 3.6. The
recommended way to install this package is via `pip
<https://pypi.python.org/pypi/pip>`_.

.. code-block:: bash

    $ git clone https://github.com/lukassup/route-cli.git
    $ pip install ./route-cli

For instructions on installing python and pip see "The Hitchhiker's Guide to
Python" `Installation Guides
<http://docs.python-guide.org/en/latest/starting/installation/>`_.

Or installing for development:

.. code-block:: bash

    $ git clone https://github.com/lukassup/route-cli.git
    $ pip install -e ./route-cli

.. _usage:

Usage
-----

.. code-block::

    $ route-cli help
    usage: route-ctl [-h]
                    {help,list,find,validate,batch-validate,batch-replace,create,update,delete}
                    ...

    positional arguments:
    {help,list,find,validate,batch-validate,batch-replace,create,update,delete}
                            subcommands
        help                show this help message and exit
        list                list all routes
        find                find routes by filter
        validate            validate a route from CLI arguments
        batch-validate      batch validate items from a JSON file
        batch-replace       batch replace items from a JSON file
        create              create or update a route
        update              update an existing rotue
        delete              delete routes by filter

    optional arguments:
    -h, --help            show this help message and exit

