.. image:: https://travis-ci.org/lukassup/route-ctl.svg?branch=master
    :target: https://travis-ci.org/lukassup/route-ctl

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

Alternatively use ``easy_install``:

.. code-block:: bash

    $ git clone https://github.com/lukassup/route-cli.git
    $ easy_install ./route-cli

.. _usage:

Usage
-----

.. code-block::

    $ route-cli help
    usage: route-ctl [-h] {help,list,find,batch-replace,batch-insert,create} ...

    positional arguments:
    {help,list,find,batch-replace,batch-insert,create}
                            subcommands
        help                show this help message and exit
        list                parse and list all routes
        find                find all routes matching criteria
        batch-replace       replace all items in destination file from a JSON file
        batch-insert        batch insert new items from a JSON file
        create              insert a new route

    optional arguments:
    -h, --help            show this help message and exit

.. _development:

Development
-----------

Install the ``route-ctl`` package in editable mode using ``pip``:

.. code-block:: bash

    $ git clone https://github.com/lukassup/route-cli.git
    $ pip install -e ./route-cli

.. _testing:

Testing
-------

Run the tests:

.. code-block:: bash

    $ git clone https://github.com/lukassup/route-cli.git
    $ cd route-cli
    $ python2 setup.py test
    $ python3 setup.py test

Or test all supported versions in Docker containers:

.. code-block:: bash

    $ git clone https://github.com/lukassup/route-cli.git
    $ make docker-build
    $ make docker-test

CentOS 6 installation with custom prefix
----------------------------------------

.. code-block:: bash

    $ cat > install-script.sh EOF
    python setup.py install --prefix=/usr/local --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
    EOF
    $ python setup.py bdist_rpm --install-script=./install-script.sh
    $ rpm -Uvh ./dist/route-ctl-*.rpm
