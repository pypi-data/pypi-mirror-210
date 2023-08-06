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
"""Input and output routines

   All input routines begin with ``load_``. All output routines begin with
   ``dump_``.

   This package also contains a ``IOData`` class to facilitate reading from
   and writing to different file formats. It contains the methods ``from_file``
   and ``to_file`` that automatically determine the file format based on the
   prefix or extension of the filename.
"""


from horton_grid.io.cube import *
from horton_grid.io.internal import *
from horton_grid.io.lockedh5 import *
from horton_grid.io.xyz import *
