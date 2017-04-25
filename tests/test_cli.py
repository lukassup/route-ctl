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
from route_ctl import _pyversion as v


if v.PY3:
    basestring = unicode = str


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
            self.assertRaises(
                SystemExit,
                cli.parser.parse_args,
                shlex.split(command),
            )
            # check exit status
            try:
                cli.parser.parse_args(shlex.split(command))
            except SystemExit as e:
                self.assertEqual(e.code, 2)
            # XXX: this always fails on Python 2 because argparse prints
            # help in str not unicode.
            # self.assertRegexpMatches(
            #     stderr.getvalue(),
            #     r'^usage:',
            # )


    def test_displays_help_with_subcommand(self):
        """CLI should display help with the `help` subcommand."""
        command = 'help'
        args = cli.parser.parse_args(shlex.split(command))
        with capture_output() as (stdout, stderr):
            # check if exits
            self.assertRaises(
                SystemExit,
                args.action,
                vars(args)
            )
            # check output
            self.assertRegexpMatches(
                stdout.getvalue(),
                r'^usage:',
            )
            # check exit status
            try:
                args.action(**vars(args))
            except SystemExit as e:
                self.assertEqual(e.code, 0)

    def test_displays_help_with_option(self):
        """CLI should display help with with `-h` option for all subcommands."""
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
                # check if exits
                self.assertRaises(
                    SystemExit,
                    cli.parser.parse_args,
                    shlex.split(command),
                )
                # check output
                self.assertRegexpMatches(
                    stdout.getvalue(),
                    r'^usage:',
                )
                # check exit code
                try:
                    cli.parser.parse_args(shlex.split(command))
                except SystemExit as e:
                    self.assertEqual(e.code, 0)
