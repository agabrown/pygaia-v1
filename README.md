# pygaia-v1
pre-Gaia EDR3 version of PyGaia

## Notes on this version of PyGaia (2020.11.21)

This is the version of the PyGaia code as it was [at the end of
2019](https://github.com/agabrown/PyGaia/commit/50f896fe14f12ffb6744d4a2e453b24abaa7e239). The following versions are
updated to the Gaia scientific performance predictions based on Gaia EDR3 (published on December 3 2020) and
extrapolations thereof. If for some reason you need to simulate the Gaia performance corresponding to the predictions
made after spacecraft commissioning, then use the code in this repository. To avoid namespace problems, the top level
package is named `pygaiav1`.

The rest of this README is (mostly) the same as in the 2019 version of PyGaia. The older science performance predictions
are not available anymore from the Gaia web pages.

## Python toolkit for basic Gaia data simulation, manipulation, and analysis

PyGaia provides python modules for the simulation of Gaia data and their errors, as well modules for the manipulation
and analysis of the Gaia catalogue data. In particular transformations between astrometric observables and phase space
variables are provided as well as transformations between sky coordinate systems. Only (very) basic functionality is
provided. Full blown simulations of Gaia data in all their gory detail requires the Java tools developed by the Gaia
Data Processing and Analysis Consortium (DPAC) in particular its Coordination Unit 2 (CU2).

This toolkit is basically an implementation of the performance models for Gaia which are publicly available at:
[http://www.cosmos.esa.int/web/gaia/science-performance](http://www.cosmos.esa.int/web/gaia/science-performance). In
addition much of the material in chapter 4 of the book [Astrometry for Astrophysics: Methods, Models, and Applications
(2012, van Altena et al.)] (http://www.cambridge.org/9780521519205) is implemented.

Note that the code in this package is __not intended for accurate astrometry applications__, such as predicting in
detail astrometric paths of stars on the sky, or transforming between observation epochs (2020.11.21: an epoch
propagation function was included in 2019).

## Documentation

All classes and methods/functions are documented so use the python help() function to find out more. More extensive
documentation will follow.

## Installation notes

This package is intended for Python3. You may experience problems if you have an older version installed. In particular
the scripts in the __examples__ folder will not run because they expect the argparse module to be present.

The following python packages are required:

* [numpy](https://numpy.org/)
* [scipy](https://scipy.org/)

For the plotting tools:

* [matplotlib](https://matplotlib.org/)
* [Cartopy](https://scitools.org.uk/cartopy/docs/latest/)

## Attribution

Please acknowledge the Gaia Project Scientist Support Team and the Gaia Data Processing and Analysis Consortium (DPAC)
if you used this code in your research.

## License

Copyright (c) 2012-2019 Anthony Brown, Leiden University, Gaia Data Processing and Analysis Consortium

PyGaia is open source and free software: you can redistribute it and/or modify it under the terms of the GNU Lesser
General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see
[http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).
