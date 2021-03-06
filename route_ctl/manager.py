# -*- coding: utf-8 -*-
"""route-ctl entry manager."""

from __future__ import absolute_import, unicode_literals, with_statement

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

    def __init__(self, filename, dict_key='routes'):
        RouteParser.__init__(self)
        RouteBuilder.__init__(self)
        self.filename = filename
        self.__log = getLogger(__name__)
        self.__key = dict_key

    def from_json(self, json_file):
        """Read items from a JSON file."""
        file_name = getattr(json_file, 'name', repr(json_file))
        self.__log.info(_('loading entries from JSON file: %r'), file_name)
        return json.load(json_file)[self.__key]

    def __items_or_json(self, items, json_file):
        """Pick either items or parse a JSON file which are mutually exclusive."""
        if json_file and not items:
            return self.from_json(json_file)
        elif items and not json_file:
            return items
        raise InvalidOperation(
            _("cannot use both arguments: 'items' and 'json_file'"))

    def list_items(self):
        """List all entries."""
        self.__log.info(_('listing all entries'))
        items = self.parse()
        return {self.__key: list(items)}

    def find_items(self, value, key, ignore_case=False, exact_match=True):
        """List entries matching key-value."""
        self.__log.info(_('listing entries matching criteria'))
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

    def _find_same(self, item, items=None, keys=('name')):
        """Find all items with matching values for given set of keys."""
        items = items if items else self.parse()
        def same(this, item=item, keys=keys):
            return all([this.get(key) == item.get(key) for key in keys])
        return filter(same, items)

    def _exists(self, item, items=None):
        """Check if an entry is already present."""
        self.__log.debug(_('checking if entry exists'))
        items = items if items else self.parse()
        found_with_same_name = any(self._find_same(item, items, keys=('name',)))
        found_with_same_net = any(self._find_same(item, items, keys=('network', 'netmask')))
        if found_with_same_name:
            self.__log.debug(_('entry with matching name exists'))
            return True
        elif found_with_same_net:
            self.__log.info(_('entry with matching subnet/netmask pair exists'))
            return True
        return False


    def create_item(self, item, force=False):
        """Create a new entry."""
        items = list(self.parse())  # eager read
        if self._exists(item, items):
            if not force:
                raise EntryAlreadyExistsError(
                    _('unable to create item. A matching entry already exists.'))
            else:
                self.__log.warning(_('forcing route entry creation (dangerous)'))
        self.__log.info(_('creating a new entry'))
        items.append(item)
        self.write(items)

    def create_items(self, items=None, json_file=None):
        """Create many entries."""
        new_items = self.__items_or_json(items, json_file)
        current_items = list(self.parse())  # eager read
        total = len(new_items)
        conflicting = 0
        added = 0
        for item in new_items:
            if self._exists(item, current_items):
                self.__log.debug(_('item already exists: %r'), json.dumps(item))
                conflicting += 1
            else:
                self.__log.info(_('adding item: %r'), json.dumps(item))
                current_items.append(item)
                added += 1
        if conflicting == total:
            self.__log.warning(_('no new entries added - all entries already exist'))
            return
        elif conflicting > 0:
            self.__log.warning(
                _('%d out of %d entries already exist (skipped)'),
                conflicting, total)
        self.__log.info(_('inserting %d entries'), added)
        self.write(current_items)

    def update_item(self, item, create=False):
        """Update an existing entry or create a new one."""
        items = list(self.parse())  # eager read
        if not self._exists(item, items):
            if not create:
                raise EntryNotFoundError(
                    _('unable to update entry. No matching entry found.'))
            self.__log.info(_('creating a new entry'))
            items.append(item)
        else:
            self.__log.info(_('updating an existing entry'))
            raise NotImplementedError(_('Not implemented'))  # TODO
        self.write(items)

    def update_items(self, items=None, json_file=None, create=True):
        """Update many entries."""
        self.__log.info(_('updating entries'))
        new_items = self.__items_or_json(items, json_file)
        current_items = list(self.parse())  # eager read
        updated = 0
        added = 0
        for item in new_items:
            if not self._exists(item, current_items):
                if not create:
                    raise EntryNotFoundError(
                        _('Unable to update entry. No matching entry found.'))
                self.__log.info(_('Creating a new entry'))
                added += 1
                current_items.append(item)
            else:
                updated += 1
                raise NotImplementedError(_('Not implemented'))  # TODO
        self.__log.info(_('Updated items: %d, added items: %d'), updated, added)
        self.write(current_items)

    def delete_items(self, key, value, ignore_case=False, exact_match=True):
        """Delete entries."""
        self.__log.info(_('Deleting entries'))
        raise NotImplementedError(_('Not implemented'))  # TODO 

    def replace(self, items=None, json_file=None):
        """Replace all entries."""
        self.__log.info(_('Replacing all entries'))
        items = self.__items_or_json(items, json_file)
        self.write(items)

    def validate_item(self, item):
        """Validate an entry."""
        self.__log.info(_('Validating an entry'))
        if not self._exists(item):
            raise EntryNotFoundError
        raise NotImplementedError(_('Not implemented'))  # TODO

    def validate_items(self, items=None, json_file=None):
        """Validate all entries."""
        self.__log.info(_('Validating entries'))
        items = self.__items_or_json(items, json_file)
        raise NotImplementedError(_('Not implemented'))  # TODO
