# -*- coding: utf-8 -*-
"""route-ctl application actions."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    with_statement,
)

import json
import logging
from gettext import translation

from .manager import RouteManager

# logging
log = logging.getLogger(__name__)

# l18n
_ = translation(__name__, 'locale', fallback=True).gettext


def list_items(route_file, *args, **kwargs):
    mgr = RouteManager(route_file)
    result = mgr.list_items()
    return json.dumps(result, indent=2)


def find_items(route_file, key, value, ignore_case, exact_match, *args,
               **kwargs):
    mgr = RouteManager(route_file)
    result = mgr.find_items(value, key, ignore_case, exact_match)
    return json.dumps(result, indent=2)


def validate_item(route_file,
                  name,
                  ensure=None,
                  gateway=None,
                  interface=None,
                  network=None,
                  netmask=None,
                  options=None,
                  *args,
                  **kwargs):
    _route = {
        'name': name,
        'ensure': ensure,
        'gateway': gateway,
        'interface': interface,
        'netmask': netmask,
        'network': network,
        'options': options,
    }
    # Drop None values to prevent unnecessary validation
    route = dict(filter(lambda item: item[1] is not None, _route.items()))
    mgr = RouteManager(route_file)
    result = mgr.validate_item(route)
    return json.dumps(result, indent=2)


def batch_create_items(route_file, source_file, *args, **kwargs):
    mgr = RouteManager(route_file)
    mgr.create_items(json_file=source_file)


def batch_update_items(route_file, source_file, *args, **kwargs):
    mgr = RouteManager(route_file)
    mgr.update_items(json_file=source_file)


def batch_validate_items(route_file, source_file, *args, **kwargs):
    mgr = RouteManager(route_file)
    result = mgr.validate_items(json_file=source_file)
    return json.dumps(result, indent=2)


def batch_replace_items(route_file, source_file, *args, **kwargs):
    mgr = RouteManager(route_file)
    mgr.replace(json_file=source_file)


def create_or_update_item(route_file,
                          name,
                          ensure,
                          gateway,
                          interface,
                          network,
                          netmask,
                          options=None,
                          *args,
                          **kwargs):
    _route = {
        'name': name,
        'ensure': ensure,
        'gateway': gateway,
        'interface': interface,
        'netmask': netmask,
        'network': network,
        'options': options,
    }
    # Drop None values
    route = dict(filter(lambda item: item[1] is not None, _route.items()))
    mgr = RouteManager(route_file)
    mgr.create_item(route)


def update_item(route_file,
                name,
                ensure,
                gateway,
                interface,
                network,
                netmask,
                options=None,
                *args,
                **kwargs):
    _route = {
        'name': name,
        'ensure': ensure,
        'gateway': gateway,
        'interface': interface,
        'netmask': netmask,
        'network': network,
        'options': options,
    }
    # Drop None values
    route = dict(filter(lambda item: item[1] is not None, _route.items()))
    mgr = RouteManager(route_file)
    mgr.update_item(route)


def delete_items(route_file, key, value, ignore_case, exact_match, *args,
                 **kwargs):
    mgr = RouteManager(route_file)
    mgr.delete_items(key, value, ignore_case, exact_match)
