# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
  author="Lukas Šupienis <lukassup@yahoo.com>",
  license="MIT",
  version="0.1.0",
  name="route-manager",
  packages=[
    "route_manager"
  ],
  entry_points={
    "console_scripts": [
      "route-cli = route_manager.cli:main"
    ],
  },
)
