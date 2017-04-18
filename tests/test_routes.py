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

class TestRouteParserValid(unittest.TestCase):
    """Perform route parsing tests for valid route file."""

    def setUp(self):
        self.route_file = StringIO(VALID_ROUTE_FILE)

    def test_parse_first_route(self):
        """First parsed route is correct."""
        self.assertEqual(
            routes.parse_route(self.route_file),
            VALID_ROUTES[0]
        )

    def test_parse_all_routes(self):
        """All of the parsed routes are correct."""
        self.assertEqual(
            list(routes.parse_routes(self.route_file)),
            VALID_ROUTES
        )


class TestRouteParserMissingCloseBrace(unittest.TestCase):
    """Perform route parsing tests for missing close brace route in file."""

    def setUp(self):
        self.route_file = StringIO(MISSING_CLOSE_BRACE_FILE)

    def test_missing_close_brace(self):
        """Correct exception is raised when missing close brace."""
        # NOTE: Python 2.6 does not understand the `assertRaises` context mgr
        self.assertRaises(
            routes.EndTokenNotFoundError,
            routes.parse_route,  # test func
            self.route_file      # arg
        )


class TestRouteParserMissingOpenBrace(unittest.TestCase):
    """Perform route parsing tests for missing open brace in file."""

    def setUp(self):
        self.route_file = StringIO(MISSING_OPEN_BRACE_FILE)

    def test_missing_open_brace(self):
        """Correct exception is raised when missing close brace."""
        # NOTE: Python 2.6 does not understand the `assertRaises` context mgr
        self.assertRaises(
            routes.StartTokenNotFoundError,
            routes.parse_route,  # test func
            self.route_file      # arg
        )
