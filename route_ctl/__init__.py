# -*- coding: utf-8 -*-

"""Sample application module."""

from __future__ import (
    absolute_import,    # 2.5+
    print_function,     # 2.6+
    unicode_literals,   # 2.6+
    with_statement,     # 2.5+
)

import logging


try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
