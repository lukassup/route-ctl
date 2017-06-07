# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    with_statement,
)

import os
import shutil
import tempfile
import unittest

from datetime import datetime

from route_ctl.builder import RouteBuilder


class TestBackup(unittest.TestCase):
    """Test backup file rotation."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.file_path = os.path.join(self.dir, 'test-file.txt')

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_rotation_with_one_backup(self):
        """One backup should be rotated."""
        now = datetime.now()
        with open(self.file_path, 'w') as fw:
            fw.write(str(now))
        backup = self.file_path + '.1'
        self.assertTrue(os.path.isfile(self.file_path))
        self.assertFalse(os.path.isfile(backup))
        RouteBuilder(self.file_path).rotate_backups(pattern='%s.%d')
        self.assertFalse(os.path.isfile(self.file_path))
        self.assertTrue(os.path.isfile(backup))
        with open(backup) as fr:
            content = fr.read()
        self.assertEqual(content, str(now))

    def test_rotation_with_two_backups(self):
        """Two backups should be rotated."""
        date_a = datetime.now()
        with open(self.file_path, 'w') as fw:
            fw.write(str(date_a))
        RouteBuilder(self.file_path).rotate_backups(pattern='%s.%d')
        date_b = datetime.now()
        with open(self.file_path, 'w') as fw:
            fw.write(str(date_b))
        RouteBuilder(self.file_path).rotate_backups(pattern='%s.%d')
        self.assertFalse(os.path.isfile(self.file_path))
        self.assertTrue(os.path.isfile(self.file_path + '.1'))
        self.assertTrue(os.path.isfile(self.file_path + '.2'))
        self.assertFalse(os.path.isfile(self.file_path + '.3'))
        self.assertFalse(os.path.isfile(self.file_path + '.4'))
        with open(self.file_path + '.2') as fr:
            content = fr.read()
        self.assertEqual(content, str(date_a))

    def test_rotation_with_above_max_backups(self):
        """Only the last N number of backups should left."""
        date_a = datetime.now()
        with open(self.file_path, 'w') as fw:
            fw.write(str(date_a))
        RouteBuilder(self.file_path).rotate_backups(pattern='%s.%d', backups=2)
        date_b = datetime.now()
        with open(self.file_path, 'w') as fw:
            fw.write(str(date_b))
        RouteBuilder(self.file_path).rotate_backups(pattern='%s.%d', backups=2)
        date_c = datetime.now()
        with open(self.file_path, 'w') as fw:
            fw.write(str(date_c))
        RouteBuilder(self.file_path).rotate_backups(pattern='%s.%d', backups=2)
        self.assertFalse(os.path.isfile(self.file_path))
        self.assertTrue(os.path.isfile(self.file_path + '.1'))
        self.assertTrue(os.path.isfile(self.file_path + '.2'))
        self.assertFalse(os.path.isfile(self.file_path + '.3'))
        with open(self.file_path + '.2') as fr:
            content = fr.read()
        self.assertEqual(content, str(date_b))

    def test_rotation_with_disabled_backups(self):
        """Rotation should not happen once backups are disabled."""
        date_a = datetime.now()
        with open(self.file_path, 'w') as fw:
            fw.write(str(date_a))
        RouteBuilder(self.file_path).rotate_backups(pattern='%s.%d', backups=0)
        self.assertTrue(os.path.isfile(self.file_path))
        self.assertFalse(os.path.isfile(self.file_path + '.1'))
        with open(self.file_path) as fr:
            content = fr.read()
        self.assertEqual(content, str(date_a))
