#!/usr/bin/env python
# -*- coding: utf-8 -*-
# HORTON-GRID: GRID for Helpful Open-source Research TOol for N-fermion systems.
# Copyright (C) 2011-2023 The HORTON-GRID Development Team
#
# This file is part of HORTON-GRID
#
# HORTON-GRID is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# HORTON-GRID is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --


import numpy as np
from glob import glob

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext


def get_sources(dirname):
    """Get all cpp files and the cext.pyx file of a package"""
    # avoid accidental inclusion of in-place build files and inc files
    result = [
        fn for fn in glob("%s/*.cpp" % dirname) if not (("ext.cpp" in fn) or ("_inc.cpp" in fn))
    ]
    result.append("%s/cext.pyx" % dirname)
    return result


def get_depends(dirname):
    """Get all files that should trigger a recompilation of the C extension of a package"""
    result = glob("%s/*.h" % dirname)
    result += glob("%s/*.pxd" % dirname)
    return result


ext_modules = [
    Extension(
        "horton_grid.cext",
        sources=get_sources("src/horton_grid"),
        depends=get_depends("src/horton_grid"),
        include_dirs=[np.get_include(), "src"],
        language="c++",
        extra_compile_args=["-std=c++11"],  # example compiler arguments
    ),
    Extension(
        "horton_grid.grid.cext",
        sources=get_sources("src/horton_grid/grid"),
        depends=get_depends("src/horton_grid/grid")
        + [
            "src/horton_grid/cell.pxd",
            "src/horton_grid/cell.h",
            "src/horton_grid/moments.pxd",
            "src/horton_grid/moments.h",
        ],
        include_dirs=[np.get_include(), "src"],
        language="c++",
        extra_compile_args=["-std=c++11"],
    ),
]

for e in ext_modules:
    e.cython_directives = {"embedsignature": True}

if __name__ == "__main__":
    setup(
        package_dir={"": "src"},
        packages=find_packages("src"),
        package_data={
            "horton_grid.data": ["data/*.*"],
            "horton_grid.data.grids": ["data/grids/*.*"],
            "horton_grid.data.test": ["data/test/*.*"],
            "horton_grid.data.examples": ["data/examples/*.py"],
        },
        include_package_data=True,
        ext_modules=ext_modules,
        cmdclass={"build_ext": build_ext},
    )
