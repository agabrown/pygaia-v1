__all__ = ['CoordinateTransformation', 'Transformations', 'EpochPropagation']

from pygaiav1.astrometry.vectorastrometry import sphericalToCartesian, cartesianToSpherical, \
        elementaryRotationMatrix, normalTriad
from pygaiav1.utils import enum, degreesToRadians, radiansToDegrees
from pygaiav1.astrometry.constants import auKmYearPerSec

from numpy import ones_like, array, pi, cos, sin, zeros_like, zeros, arccos, select
from numpy import dot, transpose, cross, vstack, diag, sqrt, identity, tile, sum, arctan
from numpy import matmul, newaxis, squeeze
from numpy.linalg import norm
from scipy import isscalar

# Obliquity of the Ecliptic (arcsec)
_obliquityOfEcliptic = degreesToRadians(84381.41100/3600.0)

# Galactic pole in ICRS coordinates (see Hipparcos Explanatory Vol 1 section 1.5, and Murray, 1983,
# section 10.2)
_alphaGalPole = degreesToRadians(192.85948)
_deltaGalPole = degreesToRadians(27.12825)
# The galactic longitude of the ascending node of the galactic plane on the equator of ICRS (see
# Hipparcos Explanatory Vol 1 section 1.5, and Murray, 1983, section 10.2)
_omega = degreesToRadians(32.93192)

# Rotation matrix for the transformation from ICRS to Galactic coordinates. See equation (4.25) in
# chapter 4.5 of "Astrometry for Astrophysics", 2012, van Altena et al.
_matA = elementaryRotationMatrix("z",pi/2.0+_alphaGalPole)
_matB = elementaryRotationMatrix("x",pi/2.0-_deltaGalPole)
_matC = elementaryRotationMatrix("z",-_omega)
_rotationMatrixIcrsToGalactic=dot(_matC,dot(_matB,_matA))

# Alternative way to calculate the rotation matrix from ICRS to Galactic coordinates. First calculate
# the vectors describing the Galactic coordinate reference frame expressed within the ICRS.
# _vecN = array([0,0,1])
# _vecG3 = array([cos(_alphaGalPole)*cos(_deltaGalPole), sin(_alphaGalPole)*cos(_deltaGalPole),
#   sin(_deltaGalPole)])
# _vecG0 = cross(_vecN,_vecG3)
# _vecG0 = _vecG0/sqrt(dot(_vecG0,_vecG0))
# _vecG1 = -sin(_omega)*cross(_vecG3,_vecG0)+cos(_omega)*_vecG0
# _vecG2 = cross(_vecG3,_vecG1)
# _rotationMatrixIcrsToGalactic=array([_vecG1,_vecG2,_vecG3])

# Rotation matrix for the transformation from Galactic to ICRS coordinates.
_rotationMatrixGalacticToIcrs = transpose(_rotationMatrixIcrsToGalactic)

# Rotation matrix for the transformation from Ecliptic to ICRS coordinates.
_rotationMatrixEclipticToIcrs = elementaryRotationMatrix("x", -1*(_obliquityOfEcliptic))

# Rotation matrix for the transformation from ICRS to Ecliptic coordinates.
_rotationMatrixIcrsToEcliptic = transpose(_rotationMatrixEclipticToIcrs)

# Rotation matrix for the transformation from Galactic to Ecliptic coordinates.
_rotationMatrixGalacticToEcliptic = dot(_rotationMatrixIcrsToEcliptic,_rotationMatrixGalacticToIcrs)

# Rotation matrix for the transformation from Ecliptic to Galactic coordinates.
_rotationMatrixEclipticToGalactic = transpose(_rotationMatrixGalacticToEcliptic)

Transformations = enum('Transformations', ['GAL2ICRS', 'ICRS2GAL', 'ECL2ICRS', 'ICRS2ECL', 'GAL2ECL', 'ECL2GAL'])

_rotationMatrixMap = {Transformations.GAL2ICRS:_rotationMatrixGalacticToIcrs,
    Transformations.ICRS2GAL:_rotationMatrixIcrsToGalactic,
    Transformations.ECL2ICRS:_rotationMatrixEclipticToIcrs,
    Transformations.ICRS2ECL:_rotationMatrixIcrsToEcliptic,
    Transformations.GAL2ECL:_rotationMatrixGalacticToEcliptic,
    Transformations.ECL2GAL:_rotationMatrixEclipticToGalactic}

_transformationStringMap = {Transformations.GAL2ICRS:("galactic", "ICRS"),
    Transformations.ICRS2GAL:("ICRS","galactic"),
    Transformations.ECL2ICRS:("ecliptic","ICRS"),
    Transformations.ICRS2ECL:("ICRS","ecliptic"),
    Transformations.GAL2ECL:("galactic","ecliptic"),
    Transformations.ECL2GAL:("ecliptic","galactic")}

def angularDistance(phi1, theta1, phi2, theta2):
    """
    Calculate the angular distance between pairs of sky coordinates.

    Parameters
    ----------

    phi1 : float
        Longitude of first coordinate (radians).
    theta1 : float
        Latitude of first coordinate (radians).
    phi2 : float
        Longitude of second coordinate (radians).
    theta2 : float
        Latitude of second coordinate (radians).

    Returns
    -------

    Angular distance in radians.
    """
    # Formula below is more numerically stable than arccos( sin(theta1)*sin(theta2) +
    # cos(phi2-phi1)*cos(theta1)*cos(theta2) )
    # See: https://en.wikipedia.org/wiki/Great-circle_distance
    return arctan( sqrt((cos(theta2)*sin(phi2-phi1))**2 +
        (cos(theta1)*sin(theta2)-sin(theta1)*cos(theta2)*cos(phi2-phi1))**2) / (sin(theta1)*sin(theta2) +
            cos(phi2-phi1)*cos(theta1)*cos(theta2)) )

class CoordinateTransformation:
    """
    Provides methods for carrying out transformations between different coordinate (reference) systems.
    Currently the following are supported:

    ICRS or Equatorial (right ascension, declination)
    Galactic (longitude, latitude)
    Ecliptic (longitude, latitude)

    The transformations can be applied to sky coordinates or Cartesian coordinates.
    """

    def __init__(self, desiredTransformation):
        """
        Class constructor/initializer. Sets the type of transformation to be used.

        Parameters
        ----------

        desiredTransformation - The kind of coordinate transformation that should be provided. For example
        Transformations.GAL2ECL
        """
        self.rotationMatrix=_rotationMatrixMap[desiredTransformation]
        self.transformationStrings=_transformationStringMap[desiredTransformation]

    def transformCartesianCoordinates(self, x, y, z):
        """
        Rotates Cartesian coordinates from one reference system to another using the rotation matrix with
        which the class was initialized. The inputs  can be scalars or 1-dimensional numpy arrays.

        Parameters
        ----------

        x - Value of X-coordinate in original reference system
        y - Value of Y-coordinate in original reference system
        z - Value of Z-coordinate in original reference system

        Returns
        -------

        xrot - Value of X-coordinate after rotation
        yrot - Value of Y-coordinate after rotation
        zrot - Value of Z-coordinate after rotation
        """
        xrot, yrot, zrot = dot(self.rotationMatrix,[x,y,z])
        return xrot, yrot, zrot

    def transformSkyCoordinates(self, phi, theta):
        """
        Converts sky coordinates from one reference system to another, making use of the rotation matrix with
        which the class was initialized. Inputs can be scalars or 1-dimensional numpy arrays.

        Parameters
        ----------

        phi   - Value of the azimuthal angle (right ascension, longitude) in radians.
        theta - Value of the elevation angle (declination, latitude) in radians.

        Returns
        -------

        phirot   - Value of the transformed azimuthal angle in radians.
        thetarot - Value of the transformed elevation angle in radians.
        """
        r=ones_like(phi)
        x, y, z = sphericalToCartesian(r, phi, theta)
        xrot, yrot, zrot = self.transformCartesianCoordinates(x, y, z)
        r, phirot, thetarot = cartesianToSpherical(xrot, yrot, zrot)
        return phirot, thetarot

    def transformProperMotions(self, phi, theta, muphistar, mutheta):
        """
        Converts proper motions from one reference system to another, using the prescriptions in section
        1.5.3 of the Hipparcos Explanatory Volume 1 (equations 1.5.18, 1.5.19).

        Parameters
        ----------

        phi       - The longitude-like angle of the position of the source (radians).
        theta     - The latitude-like angle of the position of the source (radians).
        muphistar - Value of the proper motion in the longitude-like angle, multiplied by cos(latitude).
        mutheta   - Value of the proper motion in the latitude-like angle.

        Returns
        -------

        muphistarrot - Value of the transformed proper motion in the longitude-like angle (including the
        cos(latitude) factor).
        muthetarot   - Value of the transformed proper motion in the latitude-like angle.
        """
        c, s = self._getJacobian(phi,theta)
        return c*muphistar+s*mutheta, c*mutheta-s*muphistar

    def transformSkyCoordinateErrors(self, phi, theta, sigPhiStar, sigTheta, rhoPhiTheta=0):
        """
        Converts the sky coordinate errors from one reference system to another, including the covariance
        term. Equations (1.5.4) and (1.5.20) from section 1.5 in the Hipparcos Explanatory Volume 1 are used.

        Parameters
        ----------

        phi         - The longitude-like angle of the position of the source (radians).
        theta       - The latitude-like angle of the position of the source (radians).
        sigPhiStar  - Standard error in the longitude-like angle of the position of the source (radians or
                      sexagesimal units, including cos(latitude) term)
        sigTheta    - Standard error in the latitude-like angle of the position of the source (radians or
                      sexagesimal units)

        Keywords (optional)
        -------------------

        rhoPhiTheta - Correlation coefficient of the position errors. Set to zero if this keyword is not
                      provided.

        Retuns
        ------
        
        sigPhiRotStar  - The transformed standard error in the longitude-like angle (including
                         cos(latitude) factor)
        sigThetaRot    - The transformed standard error in the latitude-like angle.
        rhoPhiThetaRot - The transformed correlation coefficient.
        """
        if isscalar(rhoPhiTheta) and not isscalar(sigTheta):
            rhoPhiTheta=zeros_like(sigTheta)+rhoPhiTheta
        c, s = self._getJacobian(phi,theta)
        cSqr = c*c
        sSqr = s*s
        covar = sigPhiStar*sigTheta*rhoPhiTheta
        varPhiStar = sigPhiStar*sigPhiStar
        varTheta = sigTheta*sigTheta
        varPhiStarRot = cSqr*varPhiStar+sSqr*varTheta+2.0*covar*c*s
        varThetaRot = sSqr*varPhiStar+cSqr*varTheta-2.0*covar*c*s
        covarRot = (cSqr-sSqr)*covar+c*s*(varTheta-varPhiStar)
        return sqrt(varPhiStarRot), sqrt(varThetaRot), covarRot/sqrt(varPhiStarRot*varThetaRot)

    def transformProperMotionErrors(self, phi, theta, sigMuPhiStar, sigMuTheta, rhoMuPhiMuTheta=0):
        """
        Converts the proper motion errors from one reference system to another, including the covariance
        term. Equations (1.5.4) and (1.5.20) from section 1.5 in the Hipparcos Explanatory Volume 1 are used.

        Parameters
        ----------

        phi             - The longitude-like angle of the position of the source (radians).
        theta           - The latitude-like angle of the position of the source (radians).
        sigMuPhiStar    - Standard error in the proper motion in the longitude-like direction (including
        cos(latitude) factor).
        sigMuTheta      - Standard error in the proper motion in the latitude-like direction.

        Keywords (optional)
        -------------------

        rhoMuPhiMuTheta - Correlation coefficient of the proper motion errors. Set to zero if this 
                          keyword is not provided.

        Retuns
        ------
        
        sigMuPhiRotStar    - The transformed standard error in the proper motion in the longitude direction
        (including cos(latitude) factor).
        sigMuThetaRot      - The transformed standard error in the proper motion in the longitude direction.
        rhoMuPhiMuThetaRot - The transformed correlation coefficient.
        """
        return self.transformSkyCoordinateErrors(phi, theta, sigMuPhiStar, sigMuTheta,
                rhoPhiTheta=rhoMuPhiMuTheta)

    def transformCovarianceMatrix(self, phi, theta, covmat):
        """
        Transform the astrometric covariance matrix to its representation in the new coordinate system.

        Parameters
        ----------

        phi       - The longitude-like angle of the position of the source (radians).
        theta     - The latitude-like angle of the position of the source (radians).
        covmat    - Covariance matrix (5x5) of the astrometric parameters.

        Returns
        -------

        covmat_rot - Covariance matrix in its representation in the new coordinate system.
        """

        c, s = self._getJacobian(phi,theta)
        jacobian = identity(5)
        jacobian[0][0]=c
        jacobian[1][1]=c
        jacobian[3][3]=c
        jacobian[4][4]=c
        jacobian[0][1]=s
        jacobian[1][0]=-s
        jacobian[3][4]=s
        jacobian[4][3]=-s

        return dot( dot(jacobian, covmat), jacobian.T )

    def _getJacobian(self, phi, theta):
        """
        Calculates the Jacobian for the transformation of the position errors and proper motion errors
        between coordinate systems. This Jacobian is also the rotation matrix for the transformation of
        proper motions. See section 1.5.3 of the Hipparcos Explanatory Volume 1 (equation 1.5.20). This
        matrix has the following form:

            |  c  s |
        J = |       |
            | -s  c |

        Parameters
        ----------

        phi       - The longitude-like angle of the position of the source (radians).
        theta     - The latitude-like angle of the position of the source (radians).

        Returns
        -------

        c, s - The Jacobian matrix elements c and s corresponding to (phi, theta) and the currently
               desired coordinate system transformation.
        """

        p, q, r = normalTriad(phi, theta)

        # zRot = z-axis of new coordinate system expressed in terms of old system
        zRot = self.rotationMatrix[2,:]

        if (p.ndim == 2):
            zRotAll = tile(zRot, p.shape[1]).reshape(p.shape[1],3)
            pRot = cross(zRotAll, r.T)
            normPRot = norm(pRot,axis=1)
            for i in range(pRot.shape[0]):
                pRot[i] = pRot[i]/normPRot[i]
            c = zeros(pRot.shape[0])
            s = zeros(pRot.shape[0])
            for i in range(pRot.shape[0]):
                c[i] = dot(pRot[i], p.T[i])
                s[i] = dot(pRot[i], q.T[i])
            return c, s
        else:
            pRot = cross(zRot, r.T)
            pRot = pRot/norm(pRot)
            return dot(pRot,p), dot(pRot,q)

class EpochPropagation:
    """
    Provides methods for transforming the astrometry and radial velocity of a given source to a different
    epoch. The formulae for rigorous epoch transformation can be found on the Gaia documentation pages:
    http://gea.esac.esa.int/archive/documentation/GDR2/Data_processing/chap_cu3ast/sec_cu3ast_intro/ssec_cu3ast_intro_tansforms.html#SSS3.P1
    """

    def __init__(self):
        self.mastorad = pi/(180*3600*1000)

    def propagate_astrometry(self, phi, theta, parallax, muphistar, mutheta, vrad, t0, t1):
        """
        Propagate the position of a source from the reference epoch t0 to the new epoch t1.

        Parameters
        ----------

        phi : float
            Longitude at reference epoch (radians).
        theta : float
            Latitude at reference epoch (radians).
        parallax : float
            Parallax at the reference epoch (mas).
        muphistar : float
            Proper motion in longitude (including cos(latitude) term) at reference epoch (mas/yr).
        mutheta : float
            Proper motion in latitude at reference epoch (mas/yr).
        vrad : float
            Radial velocity at reference epoch (km/s).
        t0 : float
            Reference epoch (Julian years).
        t1 : float
            New epoch (Julian years).

        Returns
        -------

        Astrometric parameters, including the "radial proper motion" (NOT the radial velocity), at the new epoch.
        phi1, theta1, parallax1, muphistar1, mutheta1, mur1 = epoch_prop_pos(..., t0, t1)
        """

        t = t1-t0
        p0, q0, r0 = normalTriad(phi, theta)

        # Convert input data to units of radians and Julian year. Use ICRS coordinate names internally to
        # avoid errors in translating the formulae to code.
        pmra0 = muphistar*self.mastorad
        pmdec0 = mutheta*self.mastorad
        plx0 = parallax*self.mastorad
        pmr0 = vrad*parallax/auKmYearPerSec*self.mastorad
        pmtot0sqr = (muphistar**2 + mutheta**2) * self.mastorad**2

        # Proper motion vector
        pmvec0 = pmra0*p0+pmdec0*q0

        f = (1 + 2*pmr0*t + (pmtot0sqr+pmr0**2)*t**2)**(-0.5)
        u = (r0*(1+pmr0*t) + pmvec0*t)*f

        _, phi1, theta1 = cartesianToSpherical(u[0], u[1], u[2])
        parallax1 = parallax*f
        pmr1 = (pmr0+(pmtot0sqr + pmr0**2)*t)*f**2
        pmvec1 = (pmvec0*(1+pmr0*t) - r0*pmr0**2*t)*f**3
        p1, q1, r1 = normalTriad(phi1, theta1)
        muphistar1 = sum(p1*pmvec1/self.mastorad, axis=0)
        mutheta1 = sum(q1*pmvec1/self.mastorad, axis =0)
        murad1 = pmr1/self.mastorad

        return phi1, theta1, parallax1, muphistar1, mutheta1, murad1

    def propagate_pos(self, phi, theta, parallax, muphistar, mutheta, vrad, t0, t1):
        """
        Propagate the position of a source from the reference epoch t0 to the new epoch t1.

        Parameters
        ----------

        phi : float
            Longitude at reference epoch (radians).
        theta : float
            Latitude at reference epoch (radians).
        parallax : float
            Parallax at the reference epoch (mas).
        muphistar : float
            Proper motion in longitude (including cos(latitude) term) at reference epoch (mas/yr).
        mutheta : float
            Proper motion in latitude at reference epoch (mas/yr).
        vrad : float
            Radial velocity at reference epoch (km/s).
        t0 : float
            Reference epoch (Julian years).
        t1 : float
            New epoch (Julian years).

        Returns
        -------

        Coordinates phi and theta at new epoch (in radians)
        """
        phi1, theta1, parallax1, muphistar1, mutheta1, vrad1 = self.propagate_astrometry(phi, theta, parallax, muphistar, mutheta, vrad, t0, t1)
        return phi1, theta1

    def propagate_astrometry_and_covariance_matrix(self, a0, c0, t0, t1):
        """
        Propagate the covariance matrix of the astrometric parameters and radial proper motion of a
        source from epoch t0 to epoch t1.

        Code based on the Hipparcos Fortran implementation by Lennart Lindegren.

        Parameters
        ----------

        a0 : array_like
            6-element vector: (phi, theta, parallax, muphistar, mutheta, vrad) in units of (radians,
            radians, mas, mas/yr, mas/yr, km/s). Shape of a should be (6,) or (6,N), with N the number of
            sources for which the astrometric parameters are provided.

        c0 : array_like
            Covariance matrix stored in a 6x6 element array. This can be constructed from the columns
            listed in the Gaia catalogue. The units are [mas^2, mas^2/yr, mas^2/yr^2] for the various
            elements. Note that the elements in the 6th row and column should be:
            c[6,i]=c[i,6]=c[i,3]*vrad/auKmYearPerSec for i=1,..,5 and
            c[6,6]=c[3,3]*(vrad^2+vrad_error^2)/auKmYearPerSec^2+(parallax*vrad_error/auKmYearPerSec)^2

            Shape of c0 should be (6,6) or (N,6,6).

        t0 : float
            Reference epoch (Julian years).

        t1 : float
            New epoch (Julian years).

        Returns
        -------

        Astrometric parameters, including the "radial proper motion" (NOT the radial velocity), and
        covariance matrix at the new epoch as a 2D matrix with the new variances on the diagional and the
        covariance in the off-diagonal elements.
        """

        zero, one, two, three = 0, 1, 2, 3
        tau = t1-t0

        # Calculate the normal triad [p0 q0 r0] at t0
        p0, q0, r0 = normalTriad(a0[0], a0[1])

        # Convert to internal units (radians, Julian year)
        par0 = a0[2]*self.mastorad
        pma0 = a0[3]*self.mastorad
        pmd0 = a0[4]*self.mastorad
        pmr0 = a0[5]*a0[2]/auKmYearPerSec*self.mastorad

        # Proper motion vector
        pmvec0 = pma0*p0+pmd0*q0

        # Auxiliary quantities
        tau2 = tau*tau
        pm02 = pma0**2 + pmd0**2
        w = one + pmr0*tau
        f2 = one/(one + two*pmr0*tau + (pm02+pmr0**2)*tau2)
        f = sqrt(f2)
        f3 = f2*f
        f4 = f2*f2

        # Position vector and parallax at t1
        u = (r0*w + pmvec0*tau)*f
        _, ra, dec = cartesianToSpherical(u[0], u[1], u[2])
        par = par0*f

        # Proper motion vector and radial proper motion at t1
        pmvec = (pmvec0*(one+pmr0*tau) - r0*pmr0**2*tau)*f3
        pmr = (pmr0+(pm02 + pmr0**2)*tau)*f2

        # Normal triad at t1
        p, q, r = normalTriad(ra, dec)

        # Convert parameters at t1 to external units (mas, Julian year)
        pma = sum(p*pmvec, axis=0)
        pmd = sum(q*pmvec, axis =0)

        a = zeros_like(a0)
        a[0] = ra
        a[1] = dec
        a[2] = par/self.mastorad
        a[3] = pma/self.mastorad
        a[4] = pmd/self.mastorad
        a[5] = pmr/self.mastorad

        # Auxiliary quantities for the partial derivatives

        pmz = pmvec0*f - three*pmvec*w
        pp0 = sum(p*p0, axis=0)
        pq0 = sum(p*q0, axis=0)
        pr0 = sum(p*r0, axis=0)
        qp0 = sum(q*p0, axis=0)
        qq0 = sum(q*q0, axis=0)
        qr0 = sum(q*r0, axis=0)
        ppmz = sum(p*pmz, axis=0)
        qpmz = sum(q*pmz, axis=0)

        J = zeros_like(c0)
        if (c0.ndim==2):
            J = J[newaxis,:,:]

        # Partial derivatives
        J[:,0,0] = pp0*w*f - pr0*pma0*tau*f
        J[:,0,1] = pq0*w*f - pr0*pmd0*tau*f
        J[:,0,2] = zero
        J[:,0,3] = pp0*tau*f
        J[:,0,4] = pq0*tau*f
        J[:,0,5] = -pma*tau2

        J[:,1,0] = qp0*w*f - qr0*pma0*tau*f
        J[:,1,1] = qq0*w*f - qr0*pmd0*tau*f
        J[:,1,2] = zero
        J[:,1,3] = qp0*tau*f
        J[:,1,4] = qq0*tau*f
        J[:,1,5] = -pmd*tau2

        J[:,2,0] = zero
        J[:,2,1] = zero
        J[:,2,2] = f
        J[:,2,3] = -par*pma0*tau2*f2
        J[:,2,4] = -par*pmd0*tau2*f2
        J[:,2,5] = -par*w*tau*f2

        J[:,3,0] = -pp0*pm02*tau*f3 - pr0*pma0*w*f3
        J[:,3,1] = -pq0*pm02*tau*f3 - pr0*pmd0*w*f3
        J[:,3,2] = zero
        J[:,3,3] = pp0*w*f3 - two*pr0*pma0*tau*f3 - three*pma*pma0*tau2*f2
        J[:,3,4] = pq0*w*f3 - two*pr0*pmd0*tau*f3 - three*pma*pmd0*tau2*f2
        J[:,3,5] = ppmz*tau*f2

        J[:,4,0] = -qp0*pm02*tau*f3 - qr0*pma0*w*f3
        J[:,4,1] = -qq0*pm02*tau*f3 - qr0*pmd0*w*f3
        J[:,4,2] = zero
        J[:,4,3] = qp0*w*f3 - two*qr0*pma0*tau*f3 - three*pmd*pma0*tau2*f2
        J[:,4,4] = qq0*w*f3 - two*qr0*pmd0*tau*f3 - three*pmd*pmd0*tau2*f2
        J[:,4,5] = qpmz*tau*f2

        J[:,5,0] = zero
        J[:,5,1] = zero
        J[:,5,2] = zero
        J[:,5,3] = two*pma0*w*tau*f4
        J[:,5,4] = two*pmd0*w*tau*f4
        J[:,5,5] = (w**2 - pm02*tau2)*f4

        JT = zeros_like(J)
        for i in range(J.shape[0]):
            JT[i] = J[i].T

        if (c0.ndim==2):
            c = matmul(J,matmul(c0[newaxis,:,:],JT))
        else:
            c = matmul(J,matmul(c0,JT))

        return a, squeeze(c)
