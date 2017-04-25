# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,   # Python 2.5+
    print_function,    # Python 2.6+
    unicode_literals,  # Python 2.6+
    with_statement,    # Python 2.5+
)

import unittest

try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO  # Python 2

from route_ctl import routes


VALID_ROUTE_FILE = '''\
# a comment
class netroutes::routes {               # comment
  network_route { '172.17.67.0/24':     # comment
    ensure    => 'present',             # comment
    gateway   => '10.0.2.2',            # comment
    interface => 'eth0',                # comment
    netmask   => '255.255.255.0',       # comment
    network   => '172.17.67.0',         # comment
    options   => 'table 200',           # comment
  }  # comment
  network_route { 'default':
    ensure    => 'present',
    # ensure    => 'absent',
    gateway   => '10.0.2.2',
    # gateway   => '10.0.3.3',
    interface => $appout,
    netmask   => '0.0.0.0',
    network   => 'default'
  }  # end route
}  # end file
'''

MISSING_OPEN_BRACE_FILE = '''\
# a comment
class netroutes::routes                 # comment
  network_route   '172.17.67.0/24':     # comment
    ensure    => 'present',             # comment
    gateway   => '10.0.2.2',            # comment
    interface => 'eth0',                # comment
    netmask   => '255.255.255.0',       # comment
    network   => '172.17.67.0',         # comment
    options   => 'table 200',           # comment
} # end file
'''

MISSING_CLOSE_BRACE_FILE = '''\
# a comment
class netroutes::routes {               # comment
  network_route { '172.17.67.0/24':     # comment
    ensure    => 'present',             # comment
    gateway   => '10.0.2.2',            # comment
    interface => 'eth0',                # comment
    netmask   => '255.255.255.0',       # comment
    network   => '172.17.67.0',         # comment
    options   => 'table 200',           # comment
# end file
'''

VALID_ROUTES = [
    {
        'name': '172.17.67.0/24',
        'ensure': 'present',
        'gateway': '10.0.2.2',
        'interface': 'eth0',
        'netmask': '255.255.255.0',
        'network': '172.17.67.0',
        'options': 'table 200',
    },
    {
        'name': 'default',
        'ensure': 'present',
        'gateway': '10.0.2.2',
        'interface': '$appout',
        'netmask': '0.0.0.0',
        'network': 'default',
    }
]


class TestRouteParser(unittest.TestCase):
    """Perform route parsing tests."""

    def test_parse_first_route(self):
        """First parsed route should be correct."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            self.assertEqual(routes.parse_route(route_file), VALID_ROUTES[0])

    def test_parse_all_routes(self):
        """All of the parsed routes should be correct."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            self.assertEqual(
                list(routes.parse_routes(route_file)), VALID_ROUTES)

    def test_missing_close_brace(self):
        """Correct exception should be raised when missing a close brace."""
        with StringIO(MISSING_CLOSE_BRACE_FILE) as route_file:
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(
                routes.EndTokenNotFoundError,
                routes.parse_route,  # test func
                route_file      # arg
            )

    def test_missing_open_brace(self):
        """Correct exception should be raised when missing a close brace."""
        with StringIO(MISSING_OPEN_BRACE_FILE) as route_file:
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(
                routes.StartTokenNotFoundError,
                routes.parse_route,  # test func
                route_file      # arg
            )
