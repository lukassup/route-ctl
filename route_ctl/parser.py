# -*- coding: utf-8 -*-
"""Core route parsing functionality."""

from __future__ import absolute_import, unicode_literals

import re

from contextlib import contextmanager

from . import core


ROUTE_FILE_HEADER = re.compile(
    r'''
    ^(\s*)                          # indentation
    class\ netroutes::routes\s*{    # file header token
    [^\S\n\r]*                      # any non-line-end whitespace
    (\#.*)?                         # maybe a comment
    $
    ''',
    flags=re.VERBOSE)

ROUTE_BLOCK_HEAD = re.compile(
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

ROUTE_BLOCK_BODY = re.compile(
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

CLOSE_BRACE = re.compile(
    r'''
    ^(\s*)          # indentation
    }               # closing brace
    [^\S\n\r]*      # any non-line-end whitespace
    (\#.*)?         # maybe a comment
    $
    ''',
    flags=re.VERBOSE)


class RouteParserError(core.RouteError):
    pass


class StartTokenNotFoundError(RouteParserError):
    pass


class EndTokenNotFoundError(RouteParserError):
    pass


class RouteParser(object):
    """Route parser."""

    def __init__(self,
                 lines,
                 file_header=ROUTE_FILE_HEADER,
                 block_head=ROUTE_BLOCK_HEAD,
                 block_body=ROUTE_BLOCK_BODY,
                 block_close=CLOSE_BRACE):
        self._lines = lines
        self._file_header = file_header
        self._block_head = block_head
        self._block_body = block_body
        self._block_close = block_close

    def _find_file_header(self):
        """Find the file header."""
        for line in self._lines:
            if self._file_header.match(line):
                break
        else:
            raise StartTokenNotFoundError('No match for file header.')

    def _find_close_brace(self):
        """Find the close brace."""
        for line in self._lines:
            if self._block_close.match(line):
                break
        else:
            raise EndTokenNotFoundError('No match for close brace.')

    def _find_block_start(self):
        """Find the beginning of a code block."""
        for line in self._lines:
            head_match = self._block_head.match(line)
            if head_match:
                return head_match.groupdict()
        raise StartTokenNotFoundError('No match for code block start.')

    def parse_one(self):
        """Find a route block in an iterable of strings (e.g. lines in file).

        Example:

        >>> with open('my_route_file.pp') as route_file:
        ...     parser = RouteParser(route_file)
        ...     route = parser.parse_one()
        ...     print(route)

        """
        route = self._find_block_start()
        # begin code block body parsing
        for line in self._lines:
            if self._block_close.match(line):
                break
            block_item_match = self._block_body.match(line)
            if block_item_match:
                item = block_item_match.groupdict()
                # NOTE: 'key' and 'value' named capture groups are expected
                # in the regular expression pattern
                key, value = item['key'], item['value']
                route[key] = value
        else:
            raise EndTokenNotFoundError('No match for code block end.')
        return route

    @classmethod
    def parse_all(cls, lines):
        """Itertively parse all routes in an iterable of strings (e.g. a file).

        Example:

        >>> with open('my_route_file.pp') as route_file:
        ...     for route in RouteParser.parse_all(route_file):
        ...         print(route)

        """
        return cls(lines).parse_all()

    def parse_all(self):
        """Itertively parse all routes in an iterable of strings (e.g. a file).

        Example:

        >>> with open('my_route_file.pp') as route_file:
        ...     parser = RouteParser(route_file)
        ...     for route in parser.parse_all():
        ...         print(route)

        """
        try:
            self._find_file_header()
            while True:
                yield self.parse_one()
        except StartTokenNotFoundError:
            return

    @classmethod
    @contextmanager
    def open(cls, filename, mode='r', *args, **kwargs):
        """File parser context manager.

        Example:

        >>> with RouteParser.open('my_route_file.pp') as parser:
        ...     for route in parser.parse_all():
        ...         print(route)

        """
        with open(filename, mode, *args, **kwargs) as lines:
            yield cls(lines)


if __name__ == '__main__':
    from sys import argv
    with RouteParser.open(argv[1]) as parser:
        for route in parser.parse_all():
            print(route)
