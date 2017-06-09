# -*- coding: utf-8 -*-
"""core route parsing functionality."""

from __future__ import absolute_import, unicode_literals

import re
from gettext import translation
from logging import getLogger

from . import core

# l18n
_ = translation(__name__, 'locale', fallback=True).gettext

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
                 lines=None,
                 filename=None,
                 block_head=ROUTE_BLOCK_HEAD,
                 block_body=ROUTE_BLOCK_BODY,
                 block_close=CLOSE_BRACE,
                 file_header=ROUTE_FILE_HEADER,
                 file_footer=CLOSE_BRACE):
        self.filename = filename
        self.__lines = lines
        self.__block_head = block_head
        self.__block_body = block_body
        self.__block_close = block_close
        self.__file_header = file_header
        self.__file_footer = file_footer
        self.__log = getLogger(__name__)

    def __open_file(self, filename=None):
        """Open file for reading."""
        if filename is not None:
            self.filename = filename
        elif not self.filename and not self.__lines:
            raise RouteParserError(_('Nothing to parse'))
        if self.filename and not self.__lines:
            self.__log.debug(_('Opening file for reading'))
            self.__lines = open(self.filename, mode='r')

    def __close_file(self):
        """Close file if needed."""
        if self.__lines and not self.__lines.closed:
            self.__log.debug(_('Closing file'))
            self.__lines.close()

    def __find_token(self, token):
        """Seek file until a token string is found."""
        for line in self.__lines:
            token_match = token.match(line)
            if token_match:
                return token_match.groupdict()
        raise RouteParserError

    def __find_block_start(self):
        """Find the beginning of a code block."""
        try:
            return self.__find_token(self.__block_head)
        except RouteParserError:
            raise StartTokenNotFoundError('No match for code block start.')

    def __find_block_close(self):
        """Find block closing token."""
        try:
            return self.__find_token(self.__block_close)
        except RouteParserError:
            raise EndTokenNotFoundError('No match for close brace.')

    def __find_file_header(self):
        """Find the file header."""
        try:
            return self.__find_token(self.__file_header)
        except RouteParserError:
            raise StartTokenNotFoundError('No match for file header.')

    def __find_file_footer(self):
        """Find the file footer."""
        try:
            return self.__find_token(self.__file_footer)
        except RouteParserError:
            raise EndTokenNotFoundError('No match for file footer.')

    def __parse_one(self):
        """Parse one route block."""
        route = self.__find_block_start()
        # begin code block body parsing
        for line in self.__lines:
            if self.__block_close.match(line):
                break
            block_item_match = self.__block_body.match(line)
            if block_item_match:
                item = block_item_match.groupdict()
                # NOTE: 'key' and 'value' named capture groups are expected
                # in the regular expression pattern
                key = item['key']
                value = item['value']
                route[key] = value
        else:
            raise EndTokenNotFoundError('No match for code block end.')
        return route

    def __parse_all(self):
        """Itertively parse all routes."""
        try:
            self.__log.debug(_('Seeking file until header is found'))
            self.__find_file_header()
            self.__log.debug(_('Parsing all routes'))
            while True:
                yield self.__parse_one()
        except StartTokenNotFoundError:
            self.__log.debug(_('Finished parsing routes'))
            return

    def parse(self, filename=None):
        """Itertively parse all routes in an iterable of strings or file.

        Example:

        >>> parser = RouteParser()
        ... for route in parser.parse('my_route_file.pp'):
        ...     print(route)

        """
        self.__open_file(filename=filename)
        with self.__lines:
            for item in self.__parse_all():
                yield item

    @classmethod
    def read(cls, filename):
        """Iteratively parse all routes from a file (classmethod).

        Example:

        >>> for route in RouteParser.read('my_route_file.pp'):
        ...     print(route)

        """
        for item in cls().parse(filename):
            yield item
