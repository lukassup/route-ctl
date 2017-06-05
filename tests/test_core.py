# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    with_statement,
)

import unittest

from route_ctl import core


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
        self.assertTrue(existing_routes[0] in VALID_ROUTES)
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
        self.assertTrue(existing_routes[0] in VALID_ROUTES)
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
        self.assertTrue(new_routes[0] in VALID_ROUTES)
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

    def test_route_partially_valid(self):
        """Should partially validate route."""
        partially_valid_route = {
            'name': '172.17.67.0/24',
            'ensure': 'present',
            'gateway': '192.168.0.1',  # incorrect
            'interface': 'wlan0',  # incorrect
            'netmask': '255.255.255.0',
            'network': '172.17.67.0',
            'options': 'table 200',
        }
        valid_items = core.validate_route(VALID_ROUTES, partially_valid_route)
        self.assertTrue(any(valid_items.values()))
        self.assertEqual(sum(valid_items.values()), 5)

    def test_route_completely_valid(self):
        """Should validate route completely."""
        valid_route = {
            'name': '172.17.67.0/24',
            'ensure': 'present',
            'gateway': '10.0.2.2',
            'interface': 'eth0',
            'netmask': '255.255.255.0',
            'network': '172.17.67.0',
            'options': 'table 200',
        }
        valid_items = core.validate_route(VALID_ROUTES, valid_route)
        self.assertTrue(all(valid_items.values()))
        self.assertEqual(sum(valid_items.values()), len(valid_items))

    def test_route_invalid(self):
        """Should invalidate route."""
        invalid_route = {
            'name': '192.168.0.0/24',
            'ensure': 'present',
            'gateway': '192.168.0.1',
            'interface': 'eth1',
            'netmask': '255.255.255.0',
            'network': '192.168.0.0',
        }
        valid_items = core.validate_route(VALID_ROUTES, invalid_route)
        self.assertTrue(not any(valid_items.values()))
        self.assertEqual(sum(valid_items.values()), 0)


class TestValidateRoutes(unittest.TestCase):
    """Test `validate_routes()` function."""

    def test_valdiate_routes_all_valid(self):
        """Should validate all routes successfully."""
        validated = core.validate_routes(VALID_ROUTES, VALID_ROUTES)
        for v in validated:
            self.assertTrue(all(v['output'].values()))
            self.assertEqual(sum(v['output'].values()), len(v['output']))

    def test_valdiate_routes_one_valid(self):
        """Should valdiate one route successfully."""
        pass  # TODO

    def test_validate_routes_no_valid(self):
        """Should invalidate all routes."""
        pass  # TODO
