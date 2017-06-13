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

    def test_backup(self):
        pass  # test