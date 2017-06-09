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

from . import core
from .manager import RouteManager

# logging
log = logging.getLogger(__name__)

# l18n
_ = translation(__name__, 'locale', fallback=True).gettext


def list_items(route_file, *args, **kwargs):
    mgr = RouteManager(route_file)
    result = mgr.list_items()
    return json.dumps(result, indent=2)


def find_items(route_file,
        key,
        value,
        ignore_case,
        exact_match,
        *args,
        **kwargs):
    mgr = RouteManager(route_file)
    result = mgr.find_items(value, key, ignore_case, exact_match)
    return json.dumps(result, indent=2)


def validate_item(
        route_file,
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


def batch_validate_items(route_file, source_file, *args, **kwargs):
    mgr = RouteManager(route_file)
    result = mgr.validate_items(json_file=source_file)
    return json.dumps(result, indent=2)


def batch_replace_items(route_file, source_file, *args, **kwargs):
    mgr = RouteManager(route_file)
    mgr.replace(json_file=source_file)


def create_or_update_item(
        route_file,
        name,
        ensure,
        gateway,
        interface,
        network,
        netmask,
        options=None,
        *args,
        **kwargs):
    log.debug(_('called `create_or_update_item` with arguments: route_file=%r, '
                'name=%r, ensure=%r, gateway=%r, interface=%r, network=%r, '
                'netmask=%r, options=%r, %r, %r'),
              route_file, name, ensure, gateway, interface, network, netmask,
              options, args, kwargs)
    route = {
        'name': name,
        'ensure': ensure,
        'gateway': gateway,
        'interface': interface,
        'netmask': netmask,
        'network': network,
    }
    if options:
        route['options'] = options
    mgr = RouteManager(route_file)
    current_routes = list(mgr.parse())
    log.info(_('looking up if the route already exists'))
    existing_routes = list(core.find_existing(current_routes, route))
    if not existing_routes:
        log.info(_('creating a new route %s=%r'), 'name', name)
        current_routes.append(route)
    elif len(existing_routes) > 1:
        raise core.MultipleRoutesFoundError(
            _('Unable to update. More than one route with such name exists.'))
    else:
        existing_route = existing_routes[0]
        old_name = existing_route['name']
        log.info(_('updating existing route %s=%r'), 'name', old_name)
        existing_route.update(route)
    mgr.write(current_routes)
    return json.dumps({'routes': current_routes}, indent=2)


def update_item(
        route_file,
        name,
        ensure,
        gateway,
        interface,
        network,
        netmask,
        options=None,
        *args,
        **kwargs):
    log.debug(_('called `update_item` with arguments: route_file=%r, '
                'name=%r, ensure=%r, gateway=%r, interface=%r, network=%r, '
                'netmask=%r, options=%r, %r, %r'),
              route_file, name, ensure, gateway, interface, network, netmask,
              options, args, kwargs)
    route = {
        'name': name,
        'ensure': ensure,
        'gateway': gateway,
        'interface': interface,
        'netmask': netmask,
        'network': network,
    }
    if options:
        route['options'] = options
    mgr = RouteManager(route_file)
    current_routes = list(mgr.parse())
    log.info(_('looking up if the route already exists'))
    existing_routes = list(core.find_existing(current_routes, route))
    if not existing_routes:
        raise core.RouteNotFoundError(
            _('Unable to update. No route matching criteria found.'))
    if len(existing_routes) > 1:
        raise core.MultipleRoutesFoundError(
            _('Unable to update. More than one route matching criteria exist.'))
    existing_route = existing_routes[0]
    old_name = existing_route['name']
    log.info(_('updating existing route %s=%r'), 'name', old_name)
    existing_route.update(route)
    mgr.write(current_routes)
    return json.dumps({'routes': current_routes}, indent=2)


def delete_items(
        route_file,
        key,
        value,
        ignore_case,
        exact_match,
        *args,
        **kwargs):
    mgr = RouteManager(route_file)
    mgr.delete_items(key, value, ignore_case, exact_match)
