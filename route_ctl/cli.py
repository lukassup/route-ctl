# -*- coding: utf-8 -*-
"""route-ctl command-line interface."""

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import logging
import os
import sys
from gettext import translation

from .actions import (
    batch_create_items,
    batch_replace_items,
    batch_update_items,
    create_or_update_item,
    delete_items,
    find_items,
    list_items,
    update_item,
)

# logging
log = logging.getLogger(__name__)

# l18n
_ = translation(__name__, 'locale', fallback=True).gettext


def _help(*args, **kwargs):
    parser.print_help()
    parser.exit()

# generics

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
    help=_('more verbose'),
)
log_group.add_argument(
    '-q',
    '--quiet',
    dest='verbosity',
    action='append_const',
    const=10,
    help=_('less verbose'),
)

config_args = argparse.ArgumentParser(add_help=False)
config_args.add_argument(
    '-F',
    '--route-file',
    metavar='FILE',
    dest='route_file',
    default=os.environ.get('ROUTE_FILE'),
    help=_('route file (default: ROUTE_FILE environment variable)'),
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

create_update_parser = argparse.ArgumentParser(add_help=False)
create_update_parser.add_argument(
    'name',
    metavar='NAME',
    help=_('route name'),
)
create_update_parser.add_argument(
    '-e',
    '--ensure',
    required=True,
    metavar='STATE',
    choices=['present', 'absent'],
    help=_('ensured route state'),
)
create_update_parser.add_argument(
    '-g',
    '--gateway',
    required=True,
    metavar='GATEWAY',
    help=_('route gateway'),
)
create_update_parser.add_argument(
    '-i',
    '--interface',
    required=True,
    metavar='INTERFACE',
    help=_('route egress interface'),
)
create_update_parser.add_argument(
    '-m',
    '--netmask',
    required=True,
    metavar='NETMASK',
    help=_('route destination network mask'),
)
create_update_parser.add_argument(
    '-n',
    '--network',
    required=True,
    metavar='NETWORK',
    help=_('route destination network'),
)
create_update_parser.add_argument(
    '-O',
    '--options',
    required=False,
    metavar='OPTIONS',
    help=_('additional route options'),
)

# base parser
parser = argparse.ArgumentParser()

# install subcommands
subparsers = parser.add_subparsers(help=_('subcommands'), dest='subcommand')
subparsers.required = True

# help subcommand
help_action = subparsers.add_parser(
    'help',
    help=_('show this help message and exit'),
    parents=[common_args]
)

help_action.set_defaults(action=_help)

# list subcommand
list_action = subparsers.add_parser(
    'list',
    help=_('list all routes'),
    parents=[
        common_args,
        config_args,
    ]
)
list_action.set_defaults(action=list_items)

# find subcommand
find_action = subparsers.add_parser(
    'find',
    help=_('find routes by filter'),
    parents=[
        common_args,
        config_args,
        retrieve_delete_parser,
    ]
)
find_action.set_defaults(action=find_items)

# validate subcommand
# validate_action = subparsers.add_parser(
#     'validate',
#     help=_('validate a route from CLI arguments'),
#     parents=[
#         common_args,
#         config_args,
#         create_update_parser,
#     ]
# )
# validate_action.set_defaults(action=validate_item)

# batch-validate subcommand
# batch_validate_action = subparsers.add_parser(
#     'batch-validate',
#     help=_('batch validate items from a JSON file'),
#     parents=[
#         common_args,
#         config_args,
#     ]
# )
# batch_validate_action.set_defaults(action=batch_validate_items)
# batch_validate_action.add_argument(
#     'source_file',
#     metavar='JSON_FILE',
#     type=argparse.FileType('r'),
#     help=_('JSON format file'),
# )

# batch-replace subcommand
batch_replace_action = subparsers.add_parser(
    'batch-replace',
    help=_('batch replace items from a JSON file'),
    parents=[
        common_args,
        config_args,
    ]
)
batch_replace_action.set_defaults(action=batch_replace_items)
batch_replace_action.add_argument(
    'source_file',
    metavar='JSON_FILE',
    type=argparse.FileType('r'),
    help=_('JSON file'),
)

# batch-create subcommand
batch_create_action = subparsers.add_parser(
    'batch-create',
    help=_('batch create items from a JSON file'),
    parents=[
        common_args,
        config_args,
    ]
)
batch_create_action.set_defaults(action=batch_create_items)
batch_create_action.add_argument(
    'source_file',
    metavar='JSON_FILE',
    type=argparse.FileType('r'),
    help=_('JSON file'),
)

# batch-update subcommand
# batch_update_action = subparsers.add_parser(
#     'batch-update',
#     help=_('batch update or create items from a JSON file'),
#     parents=[
#         common_args,
#         config_args,
#     ]
# )
# batch_update_action.set_defaults(action=batch_update_items)
# batch_update_action.add_argument(
#     'source_file',
#     metavar='JSON_FILE',
#     type=argparse.FileType('r'),
#     help=_('JSON file'),
# )

# create subcommand
create_action = subparsers.add_parser(
    'create',
    help=_('create or update a route'),
    parents=[
        common_args,
        config_args,
        create_update_parser,
    ]
)
create_action.set_defaults(action=create_or_update_item)

# update subcommand
# update_action = subparsers.add_parser(
#     'update',
#     help=_('update an existing rotue'),
#     parents=[
#         common_args,
#         config_args,
#         create_update_parser,
#     ]
# )
# update_action.set_defaults(action=update_item)

# delete subcommand
# delete_action = subparsers.add_parser(
#     'delete',
#     help=_('delete routes by filter'),
#     parents=[
#         common_args,
#         config_args,
#         retrieve_delete_parser,
#     ]
# )
# delete_action.set_defaults(action=delete_items)


def main():
    """CLI entrypoint."""
    from sys import exit
    args = parser.parse_args()
    log_level = max(logging.DEBUG, min(logging.CRITICAL, sum(args.verbosity)))
    debug_on = log_level <= logging.DEBUG
    logging.basicConfig(level=log_level)
    log.debug(_('Starting with cli arguments: %r'), vars(args))
    try:
        print(args.action(**vars(args)), file=args.out_file)
        exit(0)
    except Exception as e:
        log.error(e, exc_info=debug_on)
        exit(1)
