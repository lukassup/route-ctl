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

SINGLE_VALID_ROUTE_FILE = '''\
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
}
'''


MISSING_HEADER_FILE = '''\
# a comment
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


class TestFindHeader(unittest.TestCase):
    """Test `find_header()` function."""

    def test_header_present(self):
        """Should stop right after the header is found."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            try:
                routes.find_header(route_file)
            except Exception as e:
                self.fail(e)
            line = route_file.readline().rstrip()
            # should read the first line after the header
            self.assertEqual(
                line, "  network_route { '172.17.67.0/24':     # comment")

    def test_header_absent(self):
        """Should raise the correct exception if header doesn't exist."""
        with StringIO(MISSING_HEADER_FILE) as route_file:
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(
                routes.StartTokenNotFoundError,
                routes.find_header,  # test func
                route_file      # arg
            )


class TestFindClosingBrace(unittest.TestCase):
    """Test `find_closing_brace` function."""

    def test_closing_brace_present(self):
        """Should raise no exceptions if a closing brace is found."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            try:
                routes.find_closing_brace(route_file)
            except Exception as e:
                self.fail(e)

    def test_closing_brace_absent(self):
        """Correct exception should be raised when missing a close brace."""
        with StringIO(MISSING_CLOSE_BRACE_FILE) as route_file:
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(
                routes.EndTokenNotFoundError,
                routes.parse_route,  # test func
                route_file      # arg
            )


class TestParseRoute(unittest.TestCase):
    """Test `parse_route` function."""

    def test_one_route_present(self):
        """Should correctly return the parsed route."""
        with StringIO(SINGLE_VALID_ROUTE_FILE) as route_file:
            self.assertEqual(routes.parse_route(route_file), VALID_ROUTES[0])

    def test_many_routes_present(self):
        """Should correctly return the first parsed route."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            self.assertEqual(routes.parse_route(route_file), VALID_ROUTES[0])

    def test_missing_close_brace(self):
        """Should raise the correct exception when missing a close brace."""
        with StringIO(MISSING_CLOSE_BRACE_FILE) as route_file:
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(
                routes.EndTokenNotFoundError,
                routes.parse_route,  # test func
                route_file      # arg
            )

    def test_missing_open_brace(self):
        """Should raise then correct exception when missing a close brace."""
        with StringIO(MISSING_OPEN_BRACE_FILE) as route_file:
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(
                routes.StartTokenNotFoundError,
                routes.parse_route,  # test func
                route_file      # arg
            )


class TestParseRoutes(unittest.TestCase):
    """Perform route parsing tests."""

    def test_parse_all_routes(self):
        """Should parse all routes correctly."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            self.assertEqual(
                list(routes.parse_routes(route_file)), VALID_ROUTES)


class TestFindRoutes(unittest.TestCase):
    """Test `find_routes()` function."""
    pass
    # TODO


class TestFindExisting(unittest.TestCase):
    """Test `find_existing()` function."""
    pass
    # TODO


class TestDeleteRoutes(unittest.TestCase):
    """Test `delete_routes()` function."""
    pass
    # TODO


class TestValidateRoute(unittest.TestCase):
    """Test `validate_route()` function."""
    pass
    # TODO


class TestValidateRoutes(unittest.TestCase):
    """Test `validate_routes()` function."""
    pass
    # TODO

