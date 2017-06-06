# -*- coding: utf-8 -*-
"""route-ctl application module."""

import logging

try:
    from logging import NullHandler
except ImportError:
    # NOTE: PY2 compat
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())
