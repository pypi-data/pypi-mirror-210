# HORTON-GRID

The Grid used in *H*elpful *O*pen-source *R*esearch *TO*ol for *N*-fermion systems.

## Overview

HORTON-GRID is an integral grid that was initially implemented in Horton 2. This updated version now supports Python 3.10 and above.

HORTON-GRID is an essential tool used in computational chemistry. It provides functionalities for creating and manipulating molecular grids which are used in various scientific computations.

For more information, visit HORTON's website: [http://theochem.github.io/horton/latest](http://theochem.github.io/horton/latest)

:warning: The new API of `grid` in `Horton` has been changed at https://github.com/theochem/grid. The code is now purely Python and has been refactored since then. Its API has been updated to be more robust, flexible, and user-friendly, resulting in higher quality code. It is (to be) distributed under `conda` and `pip`. If you are thinking of doing active development in grid, I highly encourage you to do so at https://github.com/theochem/grid.

## Key Features

- Molecular grids for computational chemistry.
- Implemented in Python 3.10 for broad compatibility with scientific computing packages.
- Adheres to strict code formatting standards, using tools such as Black and Ruff.
- Built with a focus on scientific research and education.

## Installation

### For Users
```
pip install horton-grid
```

### For Developers
Clone the repository:

```bash
git clone git@github.com:yingxingcheng/horton-grid.git
```
Navigate to the horton-grid directory:
```bash
cd horton-grid
```
Install the package:
```bash
pip install -e .
```

## Dependencies
The horton-grid project depends on the following Python packages:

- NumPy
- pre-commit
- pytest
- nose

These dependencies will be automatically installed when you install horton-grid.
