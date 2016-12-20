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
cdir = os.path.dirname(__file__)

def readme():
    with open('{}/README.md'.format(cdir)) as f:
        return f.read()

def requirements():
    with open('{}/requirements.txt'.format(cdir)) as f:
        return [pname.strip() for pname in f.readlines()]

package_data = {
    pkg :   'cleanmask/*.py'
}

scripts = ['bin/cleanmask']

setup(name=pkg,
      version="0.0.1",
      description='Creates a binary mask given a FITS file',
      long_description=readme(),
      url='',
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
      license='GNU GPL v2',
      packages=[pkg],
      requires=requirements(),
      package_data=package_data,
      include_package_data=True,
      zip_safe=False,
      scripts = scripts,
)
