# -*- coding: utf-8 -*-
"""route-ctl entry manager."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    with_statement,
)

import json
import re
from gettext import translation
from logging import getLogger

from .builder import RouteBuilder
from .parser import RouteParser

try:
    from itertools import ifilter as filter, imap as map, izip as zip
except ImportError:
    # NOTE: import succeeds in PY2, but fails in PY3. It's fine.
    # filter, map and zip return iterators by default in PY3.
    pass

# l18n
_ = translation(__name__, 'locale', fallback=True).gettext


class RouteError(Exception):
    pass


class EntryNotFoundError(RouteError):
    pass


class MultipleEntriesFoundError(RouteError):
    pass


class InvalidEntryError(RouteError):
    pass


class EntryAlreadyExistsError(RouteError):
    pass


class InvalidOperation(RouteError):
    pass


class RouteManager(RouteParser, RouteBuilder):

    def __init__(self,
                 filename,
                 dict_key='routes'):
        RouteParser.__init__(self)
        RouteBuilder.__init__(self)
        self.filename = filename
        self.__log = getLogger(__name__)
        self.__key = dict_key

    def from_json(self, json_file):
        """Read items from a JSON file."""
        self.__log.info(_('loading entries from JSON file'))
        return json.load(json_file)[self.__key]

    def __items_or_json(self, items, json_file):
        """Mutually exclusive."""
        if json_file and not items:
            return self.from_json(json_file)
        elif items and not json_file:
            return items
        raise InvalidOperation

    def list_items(self):
        """List all entries."""
        self.__log.info(_('listing all entries'))
        items = self.parse()
        return {self.__key: list(items)}

    def find_items(self, value, key, ignore_case=False, exact_match=True):
        """List entries matching key-value."""
        self.__log.info(_('listing matching entries'))
        if not ignore_case:
            if exact_match:
                matcher = lambda item: value == item.get(key, '')
            else:
                matcher = lambda item: value in item.get(key, '')
        else:
            regexp = re.compile(value, flags=re.IGNORECASE)
            if exact_match:
                matcher = lambda item: regexp.match(item.get(key, ''))
            else:
                matcher = lambda item: regexp.search(item.get(key, ''))
        items = filter(matcher, self.parse())
        return {self.__key: list(items)}

    def exists(self, item):
        """Check if an entry is already present."""
        self.__log.debug(_('checking if entry exists'))
        raise NotImplementedError(_('Not implemented'))

    def create_item(self, item):
        """Create an entry."""
        self.__log.info(_('creating an entry'))
        if self.exists(item):
            raise EntryAlreadyExistsError
        raise NotImplementedError(_('Not implemented'))

    def create_items(self, items=None, json_file=None):
        """Create many entries."""
        self.__log.info(_('creating entries'))
        items = self.__items_or_json(items, json_file)
        raise NotImplementedError(_('Not implemented'))

    def update_item(self, item):
        """Update an entry."""
        self.__log.info(_('updating an entry'))
        if not self.exists(item):
            raise EntryNotFoundError
        raise NotImplementedError(_('Not implemented'))

    def update_items(self, items=None, json_file=None):
        """Update many entries."""
        self.__log.info(_('updating entries'))
        items = self.__items_or_json(items, json_file)
        raise NotImplementedError(_('Not implemented'))

    def delete_items(self, key, value, ignore_case=False, exact_match=True):
        """Delete entries."""
        self.__log.info(_('deleting entries'))
        raise NotImplementedError(_('Not implemented'))

    def replace(self, items=None, json_file=None):
        """Replace all entries."""
        self.__log.info(_('replacing all entries'))
        items = self.__items_or_json(items, json_file)
        self.write(items)

    def validate_item(self, item):
        """Validate an entry."""
        self.__log.info(_('validating an entry'))
        if not self.exists(item):
            raise EntryNotFoundError
        raise NotImplementedError(_('Not implemented'))

    def validate_items(self, items=None, json_file=None):
        """Validate all entries."""
        self.__log.info(_('validating entries'))
        items = self.__items_or_json(items, json_file)
        raise NotImplementedError(_('Not implemented'))
