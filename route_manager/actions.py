# -*- coding: utf-8 -*-

"""Sample application actions."""

from __future__ import (
    absolute_import,    # 2.5+
    print_function,     # 2.6+
    unicode_literals,   # 2.6+
    with_statement,     # 2.5+
)

import gettext
import json
import logging

from . import routes


# logging
log = logging.getLogger(__name__)


# l18n
trans = gettext.translation(__name__, 'locale', fallback=True)
_ = trans.gettext


# core functionality

def list_items(*args, route_file, **kwargs):
    log.info(_('listing all items'))
    result = list(routes.parse_routes(route_file))
    return json.dumps({'routes': result}, indent=2)


def find_items(*args, route_file, value, key, ignore_case, exact_match,
               **kwargs):
    log.info(_('showing items matching filter: %s=%r'), value, key)
    result = list(routes.find_routes(route_file, value, key, ignore_case, exact_match))
    return json.dumps({'routes': result}, indent=2)


def validate_item(*args, route_file, name, ensure=None, gateway=None,
                  interface=None, network=None, netmask=None, options=None,
                  **kwargs):
    route = {'name': name}
    if ensure:
        route['ensure'] = ensure
    if gateway:
        route['gateway'] = gateway
    if interface:
        route['interface'] = interface
    if netmask:
        route['netmask'] = netmask
    if network:
        route['network'] = network
    if options:
        route['options'] = options
    log.info(_('parsing routes from route file'))
    current_routes = routes.parse_routes(route_file)
    log.info(_('validating item %r'), name)
    validated = routes.validate_route(current_routes, route)
    result = {
        'input': route,
        'output': validated,
    }
    return json.dumps(result, indent=2)


def create_or_update_item(*args, route_file, name, ensure, gateway, interface,
                          network, netmask, options=None, **kwargs):
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
    log.info(_('parsing routes from route file'))
    current_routes = list(routes.parse_routes(route_file))
    log.info(_('looking up if the route already exists'))
    existing_routes = list(routes.find_existing(current_routes, route))
    if not existing_routes:
        log.info(_('creating a new route %s=%r'), 'name', name)
        current_routes.append(route)
    elif len(existing_routes) > 1:
        raise routes.MultipleRoutesFoundError(_(
                'Unable to update. '
                'More than one route with such name exists.'))
    else:
        existing_route = existing_routes[0]
        old_name = existing_route['name']
        log.info(_('updating existing route %s=%r'), 'name', old_name)
        existing_route.update(route)
    return json.dumps({'routes': current_routes}, indent=2)


def update_item(*args, route_file, name, ensure, gateway, interface, network,
                netmask, options=None, **kwargs):
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
    log.info(_('parsing routes from route file'))
    current_routes = list(routes.parse_routes(route_file))
    log.info(_('looking up if the route already exists'))
    existing_routes = list(routes.check_exists(current_routes, route))
    if not existing_routes:
        raise routes.RouteNotFoundError(_(
                'Unable to update. No route matching criteria found.'))
    if len(existing_routes) > 1:
        raise routes.MultipleRoutesFoundError(_(
                'Unable to update. '
                'More than one route matching criteria exist.'))
    existing_route = existing_routes[0]
    log.info(_('updating existing route %s=%r'), 'name', existing_route['name'])
    existing_route.update(route)
    return json.dumps({'routes': current_routes}, indent=2)


def delete_items(*args, route_file, value, key, ignore_case, exact_match,
                 **kwargs):
    log.info(_('deleting items matching filter: %s=%r'), value, key)


# CLI wrappers

def list_cli_action(*args, out_file, **kwargs):
    print(list_items(*args, **kwargs), file=out_file)


def find_cli_action(*args, out_file, **kwargs):
    print(find_items(*args, **kwargs), file=out_file)


def validate_cli_action(*args, out_file, **kwargs):
    print(validate_item(*args, **kwargs), file=out_file)


def create_cli_action(*args, out_file, **kwargs):
    print(create_or_update_item(*args, **kwargs), file=out_file)


def update_cli_action(*args, out_file, **kwargs):
    print(update_item(*args, **kwargs), file=out_file)


def delete_cli_action(*args, out_file, **kwargs):
    print(delete_items(*args, **kwargs), file=out_file)
