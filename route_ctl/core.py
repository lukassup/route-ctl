# -*- coding: utf-8 -*-
"""Core route manipulation functionality."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    with_statement,
)

import re

try:
    from itertools import ifilter as filter, imap as map, izip as zip
except ImportError:
    # NOTE: import succeeds in PY2, but fails in PY3. It's fine.
    # filter, map and zip return iterators by default in PY3.
    pass


class RouteError(Exception):
    pass


class RouteNotFoundError(RouteError):
    pass


class MultipleRoutesFoundError(RouteError):
    pass


class InvalidRouteError(RouteError):
    pass


def find_routes(routes, value, key='name', ignore_case=False, exact_match=True):
    """Itertively find all routes in an iterable of strings (e.g. a file)."""

    if exact_match and not ignore_case:
        def matcher(item, key=key, value=value):
            return value == item.get(key, '')
    else:
        flags = re.IGNORECASE if ignore_case else 0
        regexp = re.compile(value, flags=flags)
        if exact_match:
            def matcher(item, key=key, regexp=regexp):
                return regexp.match(item.get(key, ''))
        else:
            def matcher(item, key=key, regexp=regexp):
                return regexp.search(item.get(key, ''))

    return filter(matcher, routes)


def delete_routes(routes, value, key='name', ignore_case=False, exact_match=True):
    """Delete all routes matching criteria."""

    if exact_match and not ignore_case:
        def matcher(item, key=key, value=value):
            return value != item.get(key, '')
    else:
        flags = re.IGNORECASE if ignore_case else 0
        regexp = re.compile(value, flags=flags)
        if exact_match:
            def matcher(item, key=key, regexp=regexp):
                return not regexp.match(item.get(key, ''))
        else:
            def matcher(item, key=key, regexp=regexp):
                return not regexp.search(item.get(key, ''))

    return filter(matcher, routes)


def find_existing(routes, route):
    """Check if a route is already present.

    Route is considered present if the same network/netmask pair exists.
    """
    def same(item, route=route):
        return (item.get('network') == route.get('network') and
                item.get('netmask') == route.get('netmask'))
    return filter(same, routes)


def validate_route(origin_route, other_route):
    validated = {}.fromkeys(other_route, False)
    if origin_route:
        try:
            other_route['network']
            other_route['netmask']
        except KeyError:
            raise InvalidRouteError(
                'Input route must have the "network" and "netmask" keys')
        for key in other_route:
            validated[key] = other_route[key] == origin_route.get(key)
    return validated


def validate_routes(origin_routes, other_routes):
    results = []
    for other_route in other_routes:
        found_routes = list(find_existing(origin_routes, other_route))
        if not found_routes:
            return {}.fromkeys(other_route, False)
        if len(found_routes) > 1:
            raise MultipleRoutesFoundError(
                'More than one route for network address / subnet mask pair found.')
        found_route = found_routes[0]
        validated = validate_route(found_route, other_route)
        results.append({'input': other_route, 'output': validated})
    return results
