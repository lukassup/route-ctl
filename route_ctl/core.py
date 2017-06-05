# -*- coding: utf-8 -*-

"""Core route parsing and manipulation functionality."""

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


R = re.compile

FILE_HEADER = R(
    r'''
    ^(\s*)                          # indentation
    class\ netroutes::routes\s*{    # file header token
    [^\S\n\r]*                      # any non-line-end whitespace
    (\#.*)?                         # maybe a comment
    $
    ''',
    flags=re.VERBOSE)

CLOSE_BRACE = R(
    r'''
    ^(\s*)          # indentation
    }               # closing brace
    [^\S\n\r]*      # any non-line-end whitespace
    (\#.*)?         # maybe a comment
    $
    ''',
    flags=re.VERBOSE)

ROUTE_BLOCK_HEAD = R(
    r'''
    ^(\s*)                 # indentation
    network_route\s*{\s*   # route entry header
    ([\'"])                # opening quote
    (?P<name>.*?)          # value in quotes
    \2                     # closing quote
    :                      # colon
    [^\S\n\r]*             # any non-line-end whitespace
    (\#.*)?                # maybe a comment
    $
    ''',
    flags=re.VERBOSE)

ROUTE_BLOCK_ITEM = R(
    r'''
    ^(\s*)                  # indentation
    (?P<key>\S+)\s*         # Ruby hash key
    =>\s*                   # Ruby hash arrow
    ([\'"]?)                # maybe quotes
    (?P<value>.*?)          # Ruby hash value
    \3                      # closing quote
    ,?                      # maybe a comma
                            # (commas are optional for the last item)
    [^\S\n\r]*              # any non-line-end whitespace
    (\#.*)?                 # maybe a comment
    $
    ''',
    flags=re.VERBOSE)


class RouteError(Exception):
    pass


class RouteParserError(RouteError):
    pass


class RouteNotFoundError(RouteError):
    pass


class MultipleRoutesFoundError(RouteError):
    pass


class InvalidRouteError(RouteError):
    pass


class StartTokenNotFoundError(RouteParserError):
    pass


class EndTokenNotFoundError(RouteParserError):
    pass


def find_header(lines, header=FILE_HEADER):
    """Find the file header."""
    for line in lines:
        if header.match(line):
            break
    else:
        raise StartTokenNotFoundError('No match for file header.')


def find_closing_brace(lines, close_brace=CLOSE_BRACE):
    """Find the closing brace."""
    for line in lines:
        if close_brace.match(line):
            break
    else:
        raise EndTokenNotFoundError('No match for code block ending.')


def parse_route(lines,
                block_head=ROUTE_BLOCK_HEAD,
                block_item=ROUTE_BLOCK_ITEM,
                block_close=CLOSE_BRACE):
    """Find a route block in an iterable of strings (e.g. lines in file)."""
    route = {}
    # NOTE: find the begining of a code block
    for line in lines:
        head_match = block_head.match(line)
        if head_match:
            route.update(head_match.groupdict())
            break
    else:
        raise StartTokenNotFoundError('No match for code block start.')
    # NOTE: code block body parser
    for line in lines:
        if block_close.match(line):
            break
        block_item_match = block_item.match(line)
        if block_item_match:
            item = block_item_match.groupdict()
            key, value = item['key'], item['value']
            route[key] = value
    else:
        raise EndTokenNotFoundError('No match for code block end.')
    return route


def parse_routes(lines,
                 block_head=ROUTE_BLOCK_HEAD,
                 block_item=ROUTE_BLOCK_ITEM):
    """Itertively parse all routes in an iterable of strings (e.g. a file)."""
    try:
        find_header(lines)
        route = parse_route(lines, block_head, block_item)
        yield route
    except StartTokenNotFoundError:
        return
    while route:
        try:
            route = parse_route(lines, block_head, block_item)
            yield route
        except StartTokenNotFoundError:
            return


def find_routes(routes,
                value,
                key='name',
                ignore_case=False,
                exact_match=True):
    """Itertively find all routes in an iterable of strings (e.g. a file)."""

    if exact_match and not ignore_case:
        def matcher(item, key=key, value=value):
            return item.get(key) == value
    else:
        flags = re.IGNORECASE if ignore_case else 0
        regexp = re.compile(value, flags=flags)
        if exact_match:
            def matcher(item, key=key, regexp=regexp):
                return regexp.match(item.get(key))
        else:
            def matcher(item, key=key, regexp=regexp):
                return regexp.search(item.get(key))

    return filter(matcher, routes)


def delete_routes(routes,
                  value,
                  key='name',
                  ignore_case=False,
                  exact_match=True):
    """Delete all routes matching criteria."""

    if exact_match and not ignore_case:
        def no_matcher(item, key=key, value=value):
            return not item.get(key) == value
    else:
        flags = re.IGNORECASE if ignore_case else 0
        regexp = re.compile(value, flags=flags)
        if exact_match:
            def no_matcher(item, key=key, regexp=regexp):
                return not regexp.match(item.get(key))
        else:
            def no_matcher(item, key=key, regexp=regexp):
                return not regexp.search(item.get(key))

    return filter(no_matcher, routes)


def find_existing(routes, route):
    """Check if a route is already present.

    a route is already present if:
    - a route with the same name exists
    - a route with the same network/netmask exists
    """
    def same(item, route=route):
        return (
            (item.get('name') == route.get('name')) or
            (item.get('network') == route.get('network') and
             item.get('netmask') == route.get('netmask'))
        )
    return filter(same, routes)


def validate_route(current_routes, input_route):
    validated = {}.fromkeys(input_route, False)

    try:
        route_name = input_route['name']
    except KeyError:
        raise InvalidRouteError(
            'Input route must have a value for the "name" key')

    def name_matcher(item, key='name', route_name=route_name):
        return item.get(key) == route_name

    found_routes = list(filter(name_matcher, current_routes))
    if not found_routes:
        # everything should be set to False when a route is not found
        return validated
    if len(found_routes) > 1:
        raise MultipleRoutesFoundError(
            'More than one route with name {0!r} found'.format(route_name))

    found_route = found_routes[0]
    for key in input_route:
        validated[key] = input_route[key] == found_route.get(key)
    return validated


def validate_routes(current_routes, input_routes):
    results = []

    for input_route in input_routes:
        try:
            route_name = input_route['name']
        except KeyError:
            raise InvalidRouteError('Input route must have the "name" key')

        def name_matcher(item, key='name', route_name=route_name):
            return item.get(key) == route_name

        found_routes = list(filter(name_matcher, current_routes))
        if not found_routes:
            raise RouteNotFoundError(
                'No route with name {0!r}'.format(route_name))
        if len(found_routes) > 1:
            raise MultipleRoutesFoundError(
                'More than one route with name {0!r} found'.format(route_name))

        found_route = found_routes[0]
        validated = {}.fromkeys(input_route, False)
        for key in input_route:
            validated[key] = input_route[key] == found_route.get(key)
        results.append({'input': input_route, 'output': validated})
    return results
