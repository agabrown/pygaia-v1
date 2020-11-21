"""
Example usage of the plotCoordinateTransformationOnSky() function which shows
how coordinate systems such as ICRS and Galactic are related on the sky.

Anthony Brown May 2019
"""

from pygaiav1.astrometry.coordinates import Transformations
from pygaiav1.plot.sky import plotCoordinateTransformationOnSky

# Ecliptic coordinates on Galactic coordinate sky
plotCoordinateTransformationOnSky(Transformations.ECL2GAL)
