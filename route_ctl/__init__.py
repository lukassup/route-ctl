# -*- coding: utf-8 -*-
"""route-ctl application module."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    with_statement,
)

import logging

try:
    from logging import NullHandler
except ImportError:
    # NOTE: PY2 compat
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())
