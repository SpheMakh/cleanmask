#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 SKA South Africa
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import os
from setuptools import setup
import sys
pkg='cleanmask'

requirements = [
"numpy",
"astropy",
"scipy",
"scikit_image",
]

scripts = ['bin/cleanmask']

__version__ = "1.3.1"

setup(name=pkg,
      version=__version__,
      description='Creates a binary mask given a FITS image',
      url='https://github.com/SpheMakh/cleanmask',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: GNU GPL v2",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Astronomy"],
      author='Sphesihle Makhathini',
      author_email='sphemakh@gmail.com',
      license=['GNU GPL v2'],
      packages=[pkg],
      install_requires=requirements,
      zip_safe=False,
      scripts = scripts,
)
