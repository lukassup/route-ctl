# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,   # Python 2.5+
    print_function,    # Python 2.6+
    unicode_literals,  # Python 2.6+
    with_statement,    # Python 2.5+
)

import unittest
import shlex
import contextlib
import sys
import os
try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO  # Python 2

from route_ctl import cli


@contextlib.contextmanager
def capture_output():
    with StringIO() as stdout, StringIO() as stderr:
        _stdout, sys.stdout = sys.stdout, stdout
        _stderr, sys.stderr = sys.stderr, stderr
        yield stdout, stderr
        sys.stdout = _stdout
        sys.stderr = _stderr


class TestCLIParser(unittest.TestCase):
    """Perform route-ctl CLI command tests."""
    
    def test_displays_usage(self):
        """CLI displays usage without any arguments."""
        command = ''
        with capture_output() as (stdout, stderr):
            self.assertRaises(
                SystemExit,
                cli.parser.parse_args,
                shlex.split(command),
            )
            self.assertRegex(
                stderr.getvalue(),
                r'^usage:',
            )


    def test_displays_help_with_subcommand(self):
        """CLI displays help with `help` subcommand."""
        command = 'help'
        args = cli.parser.parse_args(shlex.split(command))
        with capture_output() as (stdout, stderr):
            self.assertRaises(
                SystemExit,
                args.action,
                vars(args)
            )
            self.assertRegex(
                stdout.getvalue(),
                r'^usage:',
            )

    def test_displays_help_with_option(self):
        """CLI displays help with with `-h` option."""
        commands = [
            '-h',
            'list -h',
            'find -h',
            'validate -h',
            'batch-validate -h',
            'batch-replace -h',
            'create -h',
            'update -h',
            'delete -h',
        ]
        for command in commands:
            with capture_output() as (stdout, stderr):
                self.assertRaises(
                    SystemExit,
                    cli.parser.parse_args,
                    shlex.split(command),
                )
                self.assertRegex(
                    stdout.getvalue(),
                    r'^usage:',
                )