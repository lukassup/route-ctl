# -*- coding: utf-8 -*-

from sys import version_info


PY2 = (2, 0) <= version_info < (3, 0)
PY3 = (3, 0) <= version_info < (4, 0)
PY26 = (2, 6) <= version_info < (2, 7)
PY27 = (2, 7) <= version_info < (2, 8)
PY32 = (3, 2) <= version_info < (3, 3)
PY33 = (3, 3) <= version_info < (3, 4)
PY34 = (3, 4) <= version_info < (3, 4)
PY35 = (3, 5) <= version_info < (3, 6)
PY36 = (3, 6) <= version_info < (3, 7)
