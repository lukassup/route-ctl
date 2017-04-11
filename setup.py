# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
  author="Lukas Šupienis <lukassup@yahoo.com>",
  license="MIT",
  version="0.1.0",
  name="route-ctl",
  packages=[
    "route_ctl"
  ],
  entry_points={
    "console_scripts": [
      "route-ctl = route_ctl.cli:main"
    ],
  },
)
