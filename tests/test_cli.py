# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    with_statement,
)

import contextlib
import os
import shlex
import sys
import unittest

from route_ctl import cli

try:
    from io import StringIO
except ImportError:
    # NOTE: PY2 compat
    from cStringIO import StringIO

try:
    unicode, basestring
except NameError:
    # NOTE: PY2 compat
    unicode = basestring = str


@contextlib.contextmanager
def suppress_output():
    """Pipe stdout and stderr to /dev/null."""
    with open(os.devnull, 'w') as stdout:
        with open(os.devnull, 'w') as stderr:
            _stdout, sys.stdout = sys.stdout, stdout
            _stderr, sys.stderr = sys.stderr, stderr
            yield stdout, stderr
            sys.stdout = _stdout
            sys.stderr = _stderr


@contextlib.contextmanager
def capture_output():
    """Pipe stdout and stderr to ``StringIO`` objects."""
    with StringIO() as stdout:
        with StringIO() as stderr:
            _stdout, sys.stdout = sys.stdout, stdout
            _stderr, sys.stderr = sys.stderr, stderr
            yield stdout, stderr
            sys.stdout = _stdout
            sys.stderr = _stderr


class TestCLI(unittest.TestCase):
    """Perform CLI tests."""

    def test_displays_usage(self):
        """CLI should display usage without any arguments."""
        command = ''
        with suppress_output():
            # check if exits
            self.assertRaises(SystemExit,
                              cli.parser.parse_args,
                              shlex.split(command))
            # check exit status
            try:
                cli.parser.parse_args(shlex.split(command))
            except SystemExit as err:
                self.assertEqual(err.code, 2)
            # NOTE: this always fails on Python 2 because argparse prints
            # help in str not unicode.
            # self.assertRegexpMatches(
            #     stderr.getvalue(),
            #     r'^usage:',
            # )


    def test_displays_help_with_subcommand(self):
        """CLI should display help with the `help` subcommand."""
        if sys.version_info < (2, 7):
            return
        command = 'help'
        args = cli.parser.parse_args(shlex.split(command))
        with capture_output() as (stdout, stderr):
            # check if exits
            self.assertRaises(SystemExit, args.action, vars(args))
            # check output
            self.assertRegexpMatches(stdout.getvalue(), r'^usage:')
            # check exit status
            try:
                args.action(**vars(args))
            except SystemExit as err:
                self.assertEqual(err.code, 0)

    def test_displays_help_with_option(self):
        """CLI should display help with with `-h` option for all subcommands."""
        if sys.version_info < (2, 7):
            return
        commands = [
            '-h',
            'list -h',
            'find -h',
            'batch-create -h',
            'batch-update -h',
            'batch-replace -h',
            'create -h',
            'update -h',
            'delete -h',
        ]
        for command in commands:
            with capture_output() as (stdout, stderr):
                # check if exits
                self.assertRaises(SystemExit,
                                  cli.parser.parse_args,
                                  shlex.split(command))
                # check output
                self.assertRegexpMatches(stdout.getvalue(), r'^usage:')
                # check exit code
                try:
                    cli.parser.parse_args(shlex.split(command))
                except SystemExit as err:
                    self.assertEqual(err.code, 0)
