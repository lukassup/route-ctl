# -*- coding: utf-8 -*-

"""A command-line interface module for managing Puppet routes."""

from __future__ import absolute_import, unicode_literals

import argparse
import gettext
import logging
import os
import sys

from .actions import (
    list_cli_action,
    create_cli_action,
    find_cli_action,
    validate_cli_action,
    batch_validate_cli_action,
    batch_replace_cli_action,
    update_cli_action,
    delete_cli_action,
)

# logging
log = logging.getLogger(__name__)


# l18n

trans = gettext.translation(__name__, 'locale', fallback=True)
_ = trans.gettext


# generics

parser = argparse.ArgumentParser()

common_args = argparse.ArgumentParser(add_help=False)
common_args.add_argument(
    '-o',
    '--output',
    metavar='FILE',
    dest='out_file',
    type=argparse.FileType('w'),
    default=sys.stdout,
    help=_('output file (default: stdout)'),
)
log_group = common_args.add_mutually_exclusive_group()
log_group.add_argument(
    '-v',
    '--verbose',
    dest='verbosity',
    default=[logging.WARNING],
    action='append_const',
    const=-10,
    help=_('be more verbose'),
)
log_group.add_argument(
    '-q',
    '--quiet',
    dest='verbosity',
    action='append_const',
    const=10,
    help=_('be more quiet'),
)

ro_config_args = argparse.ArgumentParser(add_help=False)
ro_config_args.add_argument(
    '-F',
    '--route-file',
    metavar='FILE',
    dest='route_file',
    type=argparse.FileType('r'),
    default=os.environ.get('ROUTE_FILE'),
    help=_('route file (default: ROUTE_FILE envvar)'),
)

rw_config_args = argparse.ArgumentParser(add_help=False)
rw_config_args.add_argument(
    '-F',
    '--route-file',
    metavar='FILE',
    dest='route_file',
    type=argparse.FileType('r+'),
    default=os.environ.get('ROUTE_FILE'),
    help=_('route file (default: ROUTE_FILE envvar)'),
)

retrieve_delete_parser = argparse.ArgumentParser(add_help=False)
retrieve_delete_parser.add_argument(
    'value',
    metavar='VALUE',
    help=_('filter by value'),
)
retrieve_delete_parser.add_argument(
    '-k',
    '--key',
    metavar='KEY',
    default='name',
    choices=[
        'name',
        'network',
        'netmask',
        'interface',
        'ensure',
        'gateway',
        'options',
    ],
    help=_('filter by key'),
)
retrieve_delete_parser.add_argument(
    '-i',
    '--ignore-case',
    action='store_true',
    default=False,
    help=_('ignore case in searches'),
)
retrieve_delete_parser.add_argument(
    '-p',
    '--partial-match',
    dest='exact_match',
    action='store_false',
    default=True,
    help=_('find partial matches'),
)

create_validate_update_parser = argparse.ArgumentParser(add_help=False)
create_validate_update_parser.add_argument(
    'name',
    metavar='NAME',
    help=_('route name'),
)
create_validate_update_parser.add_argument(
    '-e',
    '--ensure',
    required=True,
    metavar='STATE',
    choices=['present', 'absent'],
    help=_('ensured route state'),
)
create_validate_update_parser.add_argument(
    '-g',
    '--gateway',
    required=True,
    metavar='GATEWAY',
    help=_('route gateway'),
)
create_validate_update_parser.add_argument(
    '-i',
    '--interface',
    required=True,
    metavar='INTERFACE',
    help=_('route egress interface'),
)
create_validate_update_parser.add_argument(
    '-m',
    '--netmask',
    required=True,
    metavar='NETMASK',
    help=_('route destination network mask'),
)
create_validate_update_parser.add_argument(
    '-n',
    '--network',
    required=True,
    metavar='NETWORK',
    help=_('route destination network'),
)
create_validate_update_parser.add_argument(
    '-O',
    '--options',
    required=False,
    metavar='OPTIONS',
    help=_('additional route options'),
)

# install subcommands
subparsers = parser.add_subparsers(help=_('subcommands'), dest='subcommand')
subparsers.required = True

# help subcommand
help_action = subparsers.add_parser(
    'help',
    help=_('show this help message and exit'),
    parents=[
        common_args,
    ]
)
help_action.set_defaults(action=lambda *_, **__: parser.print_help())

# list subcommand
list_action = subparsers.add_parser(
    'list',
    help=_('list all routes'),
    parents=[
        common_args,
        ro_config_args,
    ]
)
list_action.set_defaults(action=list_cli_action)

# find subcommand
find_action = subparsers.add_parser(
    'find',
    help=_('find routes by filter'),
    parents=[
        common_args,
        ro_config_args,
        retrieve_delete_parser,
    ]
)
find_action.set_defaults(action=find_cli_action)

# validate subcommand
validate_action = subparsers.add_parser(
    'validate',
    help=_('validate a route from CLI arguments'),
    parents=[
        common_args,
        ro_config_args,
        create_validate_update_parser,
    ]
)
validate_action.set_defaults(action=validate_cli_action)

# batch-validate subcommand
batch_validate_action = subparsers.add_parser(
    'batch-validate',
    help=_('batch validate items from a JSON file'),
    parents=[
        common_args,
        ro_config_args,
    ]
)
batch_validate_action.set_defaults(action=batch_validate_cli_action)
batch_validate_action.add_argument(
    'source_file',
    metavar='JSON_FILE',
    type=argparse.FileType('r'),
    help=_('JSON format file'),
)

# batch-replace subcommand
batch_replace_action = subparsers.add_parser(
    'batch-replace',
    help=_('batch replace items from a JSON file'),
    parents=[
        common_args,
        ro_config_args,
    ]
)
batch_replace_action.set_defaults(action=batch_replace_cli_action)
batch_replace_action.add_argument(
    'source_file',
    metavar='JSON_FILE',
    type=argparse.FileType('r'),
    help=_('JSON format file'),
)

# create subcommand
create_action = subparsers.add_parser(
    'create',
    help=_('create or update a route'),
    parents=[
        common_args,
        rw_config_args,
        create_validate_update_parser,
    ]
)
create_action.set_defaults(action=create_cli_action)

# update subcommand
update_action = subparsers.add_parser(
    'update',
    help=_('update an existing rotue'),
    parents=[
        common_args,
        rw_config_args,
        create_validate_update_parser,
    ]
)
update_action.set_defaults(action=update_cli_action)

# delete subcommand
delete_action = subparsers.add_parser(
    'delete',
    help=_('delete routes by filter'),
    parents=[
        common_args,
        rw_config_args,
        retrieve_delete_parser,
    ]
)
delete_action.set_defaults(action=delete_cli_action)


def main():
    """CLI entrypoint."""
    args = parser.parse_args()
    log_level = max(logging.DEBUG, min(logging.CRITICAL, sum(args.verbosity)))
    debug_on = log_level <= logging.DEBUG
    logging.basicConfig(level=log_level)
    try:
        args.action(**vars(args))
    except Exception as e:
        log.exception(e, exc_info=debug_on)
