# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
  author="Lukas Šupienis <lukassup@yahoo.com>",
  license="MIT",
  url="https://github.com/lukassup/route-ctl.git",
  version="0.1.0",
  name="route-ctl",
  packages=find_packages(exclude=['tests']),
  entry_points={
    "console_scripts": [
      "route-ctl = route_ctl.cli:main"
    ],
  },
  test_suite='tests',
  zip_safe=True,
)
