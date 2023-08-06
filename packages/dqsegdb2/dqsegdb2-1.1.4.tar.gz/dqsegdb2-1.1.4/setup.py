#! -*- coding: utf-8 -*-
# DQSEGDB2
# Copyright (C) 2018,2020,2022 Cardiff University
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Setuptools script for DQSEGDB2

All of the build metadata live in pyproject.toml and setup.cfg,
this script exists _only_ to facilitate building DQSEGDB2 on platforms
where there is no PEP-517-compatible builder available.
"""

from setuptools import setup

if __name__ == "__main__":
    setup(
        use_scm_version=True,
    )
