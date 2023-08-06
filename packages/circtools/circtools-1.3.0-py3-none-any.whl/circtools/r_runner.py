#!/usr/bin/env python3

# Copyright (C) 2023 Tobias Jakobi
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


import subprocess


def _run(r_script):
    return subprocess.call(r_script, shell=True)


def circtools_circtest_wrapper():
    return _run("Rscript scripts/circtools_circtest_wrapper.R")


def another_entrypoint_if_needed():
    return _run("./scripts/some_other_script.sh")
