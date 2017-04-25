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
import shutil
import os
import string
import sys

from collections import defaultdict

from . import routes
from . import _pyversion as v


# NOTE: backward compatibility
if v.PY3:
    unicode = basestring = str

# logging
log = logging.getLogger(__name__)


# l18n
trans = gettext.translation(__name__, 'locale', fallback=True)
_ = trans.gettext


HEADER = '''\
##
#   This file was automatically generated
#

class netroutes::routes {\
'''

FOOTER = '}'

TEMPLATE = '''\
  network_route {{ {name}:
    ensure    => {ensure},
    gateway   => {gateway},
    interface => {interface},
    netmask   => {netmask},
    network   => {network},
    options   => {options},
  }}\
'''

# core functionality


class RouteFormatter(string.Formatter):
    """Silently skips missing values by inserting empty strings."""

    def __init__(self, missing='', var='$'):
        """Optionally initialized with a ``missing`` placeholder string."""
        self.missing = repr(missing)
        self.var = var

    def get_field(self, field_name, *args, **kwargs):
        """Quietly return ``None`` for missing keys and attributes."""
        try:
            value, field = super(self.__class__, self).get_field(field_name, *args, **kwargs)
        except (KeyError, AttributeError):
            return None, field_name
        # NOTE: backward compatibility -- this should reliably quotes both
        # Unicode and non-Unicode strings in Python 2 and 3.
        if (isinstance(value, basestring) and not value.startswith(self.var)):
            value = repr(str(value))
        return value, field

    def format_field(self, value, spec):
        """Insert the ``missing`` placeholder if value is falsy."""
        if value is None:
            value = self.missing
        return super(self.__class__, self).format_field(value, spec)


def do_backup(original, suffix='.backup', copy_file=shutil.copy2):
    if not os.path.exists(original) or not os.path.isfile(original):
        log.info(_('no backup needed'))
    else:
        backup = original + suffix
        log.info(_('backing up file %r -> %r'), original, backup)
        copy_file(original, backup)


def rewrite_routes(
        routes,
        route_file,
        backup=True,
        header=HEADER,
        template=TEMPLATE,
        footer=FOOTER):
    entry_fmt = RouteFormatter()
    if backup:
        do_backup(route_file)
    log.info(_('rewriting routes to file %r'), route_file)
    with open(route_file, 'w') as fw:
        if header:
            print(header, file=fw)
        for route in routes:
            print(entry_fmt.format(template, **route), file=fw)
        if footer:
            print(footer, file=fw)


def list_items(route_file, *args, **kwargs):
    current_routes = routes.parse_routes(route_file)
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
    current_routes = routes.parse_routes(route_file)
    log.info(_('creating a route filter: %s=%r'), key, value)
    found_routes = routes.find_routes(current_routes, value, key,
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
    current_routes = routes.parse_routes(route_file)
    log.info(_('validating item %r'), name)
    validated = routes.validate_route(current_routes, route)
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
    current_routes = routes.parse_routes(route_file)
    log.info(_('batch validating routes'))
    validated = routes.validate_routes(current_routes, src_routes)
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
    rewrite_routes(src_routes, route_file)
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
    with open(route_file) as fr:
        current_routes = list(routes.parse_routes(fr))
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
    rewrite_routes(current_routes, route_file)
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
    with open(route_file) as fr:
        current_routes = list(routes.parse_routes(fr))
    log.info(_('looking up if the route already exists'))
    existing_routes = list(routes.find_existing(current_routes, route))
    if not existing_routes:
        raise routes.RouteNotFoundError(_(
                'Unable to update. No route matching criteria found.'))
    if len(existing_routes) > 1:
        raise routes.MultipleRoutesFoundError(_(
                'Unable to update. '
                'More than one route matching criteria exist.'))
    existing_route = existing_routes[0]
    old_name = existing_route['name']
    log.info(_('updating existing route %s=%r'), 'name', old_name)
    existing_route.update(route)
    rewrite_routes(current_routes, route_file)
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
    with open(route_file) as fr:
        current_routes = routes.parse_routes(fr)
        log.info(_('parsing routes from route file'))
        log.info(_('filtering out items matching filter: %s=%r'), key, value)
        new_routes = list(routes.delete_routes(current_routes, value, key,
                                               ignore_case, exact_match))
    rewrite_routes(new_routes, route_file)
    result = {'routes': new_routes}
    return json.dumps(result, indent=2)


# CLI wrappers

def list_cli_action(out_file, *args, **kwargs):
    print(list_items(*args, **kwargs), file=out_file)


def find_cli_action(out_file, *args, **kwargs):
    print(find_items(*args, **kwargs), file=out_file)


def validate_cli_action(out_file, *args, **kwargs):
    print(validate_item(*args, **kwargs), file=out_file)


def batch_validate_cli_action(out_file, *args, **kwargs):
    print(batch_validate_items(*args, **kwargs), file=out_file)


def batch_replace_cli_action(out_file, *args, **kwargs):
    print(batch_replace_items(*args, **kwargs), file=out_file)


def create_cli_action(out_file, *args, **kwargs):
    print(create_or_update_item(*args, **kwargs), file=out_file)


def update_cli_action(out_file, *args, **kwargs):
    print(update_item(*args, **kwargs), file=out_file)


def delete_cli_action(out_file, *args, **kwargs):
    print(delete_items(*args, **kwargs), file=out_file)
