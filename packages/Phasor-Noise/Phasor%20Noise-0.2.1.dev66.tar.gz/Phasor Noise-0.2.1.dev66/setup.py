#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
    Phasor Noise API

"""

import os
from setuptools import setup
from pathlib import Path


setup(
    setup_requires=['pbr>=5.6.0'],
    pbr=True
)

"""
Setup the default configuration directory and images directory
"""
for path in [Path(os.path.expanduser("~/phasor-generator/config")), Path(os.path.expanduser("~/phasor-generator/images"))]:
    if not os.path.exists(path):
        path.mkdir(parents=True)
