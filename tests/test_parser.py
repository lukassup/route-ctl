# -*- coding: utf-8 -*-

"""Route parser tests."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    with_statement,
)

import unittest

try:
    from io import StringIO
except ImportError:
    # NOTE: PY2 compat
    from cStringIO import StringIO

from route_ctl.parser import (
    RouteParser,
    StartTokenNotFoundError,
    EndTokenNotFoundError,
)


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
    """Test `_find_file_header` method."""

    def test_header_present(self):
        """Should stop right after the header is found."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            parser = RouteParser(route_file)
            try:
                parser._find_file_header()
            except Exception as err:
                self.fail(err)
            line = route_file.readline().rstrip()
            # should read the first line after the header
            self.assertEqual(
                line, "  network_route { '172.17.67.0/24':     # comment")

    def test_header_absent(self):
        """Should raise the correct exception if header doesn't exist."""
        with StringIO(MISSING_HEADER_FILE) as route_file:
            parser = RouteParser(route_file)
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(StartTokenNotFoundError, parser._find_file_header)


class TestFindClosingBrace(unittest.TestCase):
    """Test `_find_close_brace` method."""

    def test_closing_brace_present(self):
        """Should raise no exceptions if a closing brace is found."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            parser = RouteParser(route_file)
            try:
                parser._find_close_brace()
            except Exception as err:
                self.fail(err)

    def test_closing_brace_absent(self):
        """Correct exception should be raised when missing a close brace."""
        with StringIO(MISSING_CLOSE_BRACE_FILE) as route_file:
            parser = RouteParser(route_file)
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(EndTokenNotFoundError, parser.parse_one)


class TestParseRoute(unittest.TestCase):
    """Test `parse_one` method."""

    def test_one_route_present(self):
        """Should correctly return the parsed route."""
        with StringIO(SINGLE_VALID_ROUTE_FILE) as route_file:
            parser = RouteParser(route_file)
            self.assertEqual(parser.parse_one(), VALID_ROUTES[0])

    def test_many_routes_present(self):
        """Should correctly return the first parsed route."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            parser = RouteParser(route_file)
            self.assertEqual(parser.parse_one(), VALID_ROUTES[0])

    def test_missing_close_brace(self):
        """Should raise the correct exception when missing a close brace."""
        with StringIO(MISSING_CLOSE_BRACE_FILE) as route_file:
            parser = RouteParser(route_file)
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(EndTokenNotFoundError, parser.parse_one)

    def test_missing_open_brace(self):
        """Should raise then correct exception when missing a close brace."""
        with StringIO(MISSING_OPEN_BRACE_FILE) as route_file:
            parser = RouteParser(route_file)
            # NOTE: there is no context manager for ``assertRaises``` in PY26.
            self.assertRaises(StartTokenNotFoundError, parser.parse_one)


class TestParseRoutes(unittest.TestCase):
    """Perform route parsing tests."""

    def test_parse_all_routes(self):
        """Should parse all routes correctly."""
        with StringIO(VALID_ROUTE_FILE) as route_file:
            parser = RouteParser(route_file)
            self.assertEqual(list(parser.parse_all()), VALID_ROUTES)
