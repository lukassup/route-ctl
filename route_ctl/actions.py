# -*- coding: utf-8 -*-
"""route-ctl application actions."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    with_statement,
)

import gettext
import json
import logging

from . import core
from .builder import RouteBuilder
from .parser import RouteParser

# logging
log = logging.getLogger(__name__)

# l18n
trans = gettext.translation(__name__, 'locale', fallback=True)
_ = trans.gettext


def write_routes(routes, route_file):
    builder = RouteBuilder()
    log.info(_('writing routes to file %r'), route_file)
    builder.write(routes, dest_filename=route_file)


def list_items(route_file, *args, **kwargs):
    parser = RouteParser(route_file)
    current_routes = parser.parse_all()
    log.info(_('parsing routes from route file'))
    result = {'routes': list(current_routes)}
    log.info(_('listing all items'))
    return json.dumps(result, indent=2)


def find_items(
        route_file,
        value,
        key,
        ignore_case,
        exact_match,
        *args,
        **kwargs):
    parser = RouteParser(route_file)
    current_routes = parser.parse_all()
    log.info(_('creating a route filter: %s=%r'), key, value)
    found_routes = core.find_routes(current_routes, value, key,
                                    ignore_case, exact_match)
    log.info(_('parsing routes from route file'))
    result = {'routes': list(found_routes)}
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
    parser = RouteParser(route_file)
    current_routes = parser.parse_all()
    log.info(_('validating item %r'), name)
    validated = core.validate_route(current_routes, route)
    result = {'input': route, 'output': validated}
    return json.dumps(result, indent=2)


def batch_validate_items(
        route_file,
        source_file,
        *args,
        **kwargs):
    log.info(_('loading routes from JSON'))
    src_routes = json.load(source_file)['routes']
    log.info(_('parsing routes from route file'))
    parser = RouteParser(route_file)
    current_routes = parser.parse_all()
    log.info(_('batch validating routes'))
    validated = core.validate_routes(current_routes, src_routes)
    result = {'routes': list(validated)}
    return json.dumps(result, indent=2)


def batch_replace_items(
        route_file,
        source_file,
        *args,
        **kwargs):
    log.info(_('loading routes from JSON'))
    src_routes = list(json.load(source_file)['routes'])
    log.info(_('batch replacing routes'))
    write_routes(src_routes, route_file)
    result = {'routes': src_routes}
    return json.dumps(result, indent=2)


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
    log.info(_('parsing routes from route file'))
    with RouteParser.open(route_file) as parser:
        current_routes = list(parser.parse_all())
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
    write_routes(current_routes, route_file)
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
    log.info(_('parsing routes from route file'))
    with RouteParser.open(route_file) as parser:
        current_routes = list(parser.parse_all())
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
    write_routes(current_routes, route_file)
    return json.dumps({'routes': current_routes}, indent=2)


def delete_items(
        route_file,
        value,
        key,
        ignore_case,
        exact_match,
        *args,
        **kwargs):
    log.debug(_('called `delete_items` with arguments: route_file=%r, '
                'value=%r, key=%r, ignore_case=%r, exact_match=%r, %r, %r'),
              route_file, value, key, ignore_case, exact_match, args, kwargs)
    with RouteParser.open(route_file) as parser:
        log.info(_('parsing routes from route file'))
        current_routes = list(parser.parse_all())
        log.info(_('filtering out items matching filter: %s=%r'), key, value)
        new_routes = list(core.delete_routes(current_routes, value, key,
                                             ignore_case, exact_match))
    write_routes(new_routes, route_file)
    result = {'routes': new_routes}
    return json.dumps(result, indent=2)
