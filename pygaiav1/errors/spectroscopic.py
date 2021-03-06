__all__ = ['vradErrorSkyAvg']

from numpy import exp, isscalar, zeros_like
from .astrometric import errorScalingMissionLength

_vradErrorACoeff = {'B0V': 0.90, 'B5V': 0.90, 'A0V': 1.0, 'A5V': 1.15, 'F0V': 1.15, 'G0V': 1.15, 'G5V': 1.15,
                    'K0V': 1.15, 'K1IIIMP': 1.15, 'K4V': 1.15, 'K1III': 1.15}
_vradErrorBCoeff = {'B0V': 50.00, 'B5V': 26.00, 'A0V': 5.50, 'A5V': 4.00, 'F0V': 1.50, 'G0V': 0.70, 'G5V': 0.60,
                    'K0V': 0.50, 'K1IIIMP': 0.39, 'K4V': 0.29, 'K1III': 0.21}
_vradCalibrationFloor = 0.5
_vradMagnitudeZeroPoint = 12.7


def vradErrorSkyAvg(vmag, spt, extension=0.0):
    """
    Calculate radial velocity error from V and the spectral type. The value of the error is an average over
    the sky.

    Parameters
    ----------

    vmag : Value(s) of V-band magnitude.
    spt  : String or array of strings representing the spectral type of the star.

    Keywords
    --------

    extension : Add this amount of years to the mission lifetime and scale the errors accordingly. Value can be
      negative for shorter mission spans (early data releases).

    Returns
    -------

    The radial velocity error in km/s.
    """
    errscaling = errorScalingMissionLength(extension, -0.5)
    if isscalar(spt):
        return _vradCalibrationFloor + _vradErrorBCoeff[spt] * exp(
            _vradErrorACoeff[spt] * (vmag - _vradMagnitudeZeroPoint)) * errscaling
    else:
        uncertainties = zeros_like(vmag)
        for i, v, s in zip(range(vmag.size), vmag, spt):
            uncertainties[i] = _vradCalibrationFloor + _vradErrorBCoeff[s] * exp(
                _vradErrorACoeff[s] * (v - _vradMagnitudeZeroPoint)) * errscaling
        return uncertainties
