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

from route_ctl import core


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
                core.find_header(route_file)
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
                core.StartTokenNotFoundError,
                core.find_header,  # test func
                route_file      # arg
            )


class TestFindClosingBrace(unittest.TestCase):
    """Test `find_closing_brace` function."""

    def test_closing_brace_present(self):
        """Should raise no exceptions if a closing brace is found."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            try:
                core.find_closing_brace(route_file)
            except Exception as e:
                self.fail(e)

    def test_closing_brace_absent(self):
        """Correct exception should be raised when missing a close brace."""
        with StringIO(MISSING_CLOSE_BRACE_FILE) as route_file:
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(
                core.EndTokenNotFoundError,
                core.parse_route,  # test func
                route_file      # arg
            )


class TestParseRoute(unittest.TestCase):
    """Test `parse_route` function."""

    def test_one_route_present(self):
        """Should correctly return the parsed route."""
        with StringIO(SINGLE_VALID_ROUTE_FILE) as route_file:
            self.assertEqual(core.parse_route(route_file), VALID_ROUTES[0])

    def test_many_routes_present(self):
        """Should correctly return the first parsed route."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            self.assertEqual(core.parse_route(route_file), VALID_ROUTES[0])

    def test_missing_close_brace(self):
        """Should raise the correct exception when missing a close brace."""
        with StringIO(MISSING_CLOSE_BRACE_FILE) as route_file:
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(
                core.EndTokenNotFoundError,
                core.parse_route,  # test func
                route_file      # arg
            )

    def test_missing_open_brace(self):
        """Should raise then correct exception when missing a close brace."""
        with StringIO(MISSING_OPEN_BRACE_FILE) as route_file:
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(
                core.StartTokenNotFoundError,
                core.parse_route,  # test func
                route_file      # arg
            )


class TestParseRoutes(unittest.TestCase):
    """Perform route parsing tests."""

    def test_parse_all_routes(self):
        """Should parse all routes correctly."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            self.assertEqual(
                list(core.parse_routes(route_file)), VALID_ROUTES)


class TestFindRoutes(unittest.TestCase):
    """Test `find_routes()` function."""

    def test_find_route_by_name_exact(self):
        """Should find a route with an exact name match."""
        expected_result = {
            'name': 'default',
            'ensure': 'present',
            'gateway': '10.0.2.2',
            'interface': '$appout',
            'netmask': '0.0.0.0',
            'network': 'default'
        }
        found_routes = list(core.find_routes(VALID_ROUTES, 'default'))
        self.assertEqual(len(found_routes), 1)
        self.assertEqual(found_routes[0], expected_result)

    def test_find_route_by_name_nocase(self):
        """Should find a route with an exact case-insensitive name match."""
        expected_result = {
            'name': 'default',
            'ensure': 'present',
            'gateway': '10.0.2.2',
            'interface': '$appout',
            'netmask': '0.0.0.0',
            'network': 'default'
        }
        found_routes = list(core.find_routes(VALID_ROUTES, 'DEFAULT', ignore_case=True))
        self.assertEqual(len(found_routes), 1)
        self.assertEqual(found_routes[0], expected_result)

    def test_find_route_regex(self):
        """Should find all routes with a regexp match."""
        found_routes = list(core.find_routes(VALID_ROUTES, '.*', exact_match=False))
        self.assertEqual(len(found_routes), len(VALID_ROUTES))
        self.assertEqual(found_routes, VALID_ROUTES)

    def test_find_route_no_match(self):
        """Should not find any routes."""
        expected_result = {
            'name': 'default',
            'ensure': 'present',
            'gateway': '10.0.2.2',
            'interface': '$appout',
            'netmask': '0.0.0.0',
            'network': 'default'
        }
        found_routes = list(core.find_routes(VALID_ROUTES, '1.2.3.4'))
        self.assertEqual(len(found_routes), 0)


class TestFindExisting(unittest.TestCase):
    """Test `find_existing()` function."""

    def test_find_existing_by_name(self):
        """Should find an existing route by with the same name."""
        expected_route = {
            'name': 'default',  # this should match
            'ensure': 'absent',
            'gateway': '192.168.0.1',
            'interface': 'wlan0',
            'netmask': '255.0.0.0',
            'network': '1.0.0.0'
        }
        existing_routes = list(core.find_existing(
            VALID_ROUTES, expected_route))
        self.assertEqual(len(existing_routes), 1)
        self.assertIn(existing_routes[0], VALID_ROUTES)
        self.assertEqual(existing_routes[0], VALID_ROUTES[1])

    def test_find_existing_by_net(self):
        """Should find and existing route with the same network/netmask pair."""
        expected_route = {
            'name': 'my-network',
            'ensure': 'absent',
            'gateway': '192.168.0.1',
            'interface': 'wlan0',
            'netmask': '0.0.0.0',  # this...
            'network': 'default',  # ...and this should match
        }
        existing_routes = list(core.find_existing(VALID_ROUTES, expected_route))
        self.assertEqual(len(existing_routes), 1)
        self.assertIn(existing_routes[0], VALID_ROUTES)
        self.assertEqual(existing_routes[0], VALID_ROUTES[1])

    def test_find_existing_absent(self):
        """Should not find any existing routes."""
        not_expected_route = {
            'name': 'random-network',
            'ensure': 'present',
            'gateway': '192.168.0.1',
            'interface': 'eth0',
            'netmask': '255.255.128.0',
            'network': '22.33.44.0',
        }
        existing_routes = list(core.find_existing(
            VALID_ROUTES, not_expected_route))
        self.assertEqual(len(existing_routes), 0)


class TestDeleteRoutes(unittest.TestCase):
    """Test `delete_routes()` function."""

    def test_delete_one_route_exact(self):
        """Should delete one route by an exact name match."""
        new_routes = list(core.delete_routes(VALID_ROUTES, 'default'))
        self.assertEqual(len(new_routes), 1)
        self.assertIn(new_routes[0], VALID_ROUTES)
        self.assertEqual(new_routes[0], VALID_ROUTES[0])

    def test_delete_all_by_regex(self):
        """Should delete all routes by a regexp match."""
        new_routes = list(core.delete_routes(VALID_ROUTES, '.*', exact_match=False))
        self.assertEqual(len(new_routes), 0)

    def test_delete_one_nocase(self):
        """Should delete one route with a case-insensitive match."""
        new_routes = list(core.delete_routes(VALID_ROUTES, 'DEFAULT', ignore_case=True))
        self.assertEqual(len(new_routes), 1)
        self.assertEqual(new_routes[0], VALID_ROUTES[0])

    def test_delete_none(self):
        """Should not delete anything (no matches)."""
        new_routes = list(core.delete_routes(VALID_ROUTES, 'non-existing-route'))
        self.assertEqual(len(new_routes), 2)
        self.assertEqual(new_routes, VALID_ROUTES)


class TestValidateRoute(unittest.TestCase):
    """Test `validate_route()` function."""
    pass
    # TODO


class TestValidateRoutes(unittest.TestCase):
    """Test `validate_routes()` function."""
    pass
    # TODO
