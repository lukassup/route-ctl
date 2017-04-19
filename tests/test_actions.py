# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,   # Python 2.5+
    print_function,    # Python 2.6+
    unicode_literals,  # Python 2.6+
    with_statement,    # Python 2.5+
)

import unittest
import tempfile
import os
import shutil

from route_ctl import actions


class TestBackup(unittest.TestCase):
    """Test backup file creation."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        self.path = os.path.join(self.dir, 'test-file.txt')
        self.expected_content = chars
        with open(self.path, 'w') as fw:
            fw.write(self.expected_content)
        self.suffix = '.backup'
        self.backup = self.path + self.suffix

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_backup_existing_file(self):
        """Existing files should be backed up."""
        self.assertTrue(os.path.isfile(self.path))
        self.assertFalse(os.path.isfile(self.backup))
        actions.do_backup(self.path, suffix=self.suffix)
        self.assertTrue(os.path.isfile(self.path))
        self.assertTrue(os.path.isfile(self.backup))
        with open(self.backup) as fr:
            content = fr.read()
            self.assertEqual(content, self.expected_content)

    def test_backup_non_existing_file(self):
        """Non-existing files should not be backed up."""
        _path = os.path.join(self.dir, 'no-such-file.txt')
        _backup = _path + self.suffix
        self.assertFalse(os.path.isfile(_path))
        self.assertFalse(os.path.isfile(_backup))
        actions.do_backup(_path, suffix=self.suffix)
        self.assertFalse(os.path.isfile(_path))
        self.assertFalse(os.path.isfile(_backup))

    def test_backup_dir(self):
        """Directories should not be backed up."""
        _path = self.dir
        _backup = _path + self.suffix
        self.assertTrue(os.path.isdir(_path))
        self.assertFalse(os.path.isdir(_backup))
        actions.do_backup(_path, suffix=self.suffix)
        self.assertTrue(os.path.isdir(_path))
        self.assertFalse(os.path.isdir(_backup))

    def test_backup_overwrite(self):
        """Last backup should be overwritten."""
        new_content = 'SOME NEW CONTENT'
        actions.do_backup(self.path, suffix=self.suffix)
        self.assertTrue(os.path.isfile(self.path))
        self.assertTrue(os.path.isfile(self.backup))
        with open(self.backup) as fr:
            content = fr.read()
            self.assertEqual(content, self.expected_content)
        with open(self.path, 'w') as fw:
            fw.write(new_content)
        actions.do_backup(self.path, suffix=self.suffix)
        self.assertTrue(os.path.isfile(self.backup))
        with open(self.backup) as fr:
            content = fr.read()
            self.assertEqual(content, new_content)
