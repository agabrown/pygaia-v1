"""
Unit tests for the utils module.
"""

import numpy as np

from numpy.testing import TestCase, assert_allclose, assert_array_almost_equal, assert_almost_equal
from numpy.testing import assert_array_less, assert_equal

from pygaiav1.utils import construct_covariance_matrix
from pygaiav1.astrometry.constants import auKmYearPerSec

class test_utils(TestCase):

    def test_construct_covariance_matrix_onesource(self):
        """
        Check that the covariance matrix is constructed correctly from the inputs provided.
        """

        cvec = np.arange(15)+1
        parallax = 16
        vrad = 17*auKmYearPerSec
        vrad_error = 18*auKmYearPerSec

        cmat = construct_covariance_matrix(cvec, parallax, vrad, vrad_error)

        self.assertEquals(6, cmat.shape[0])
        self.assertEquals(6, cmat.shape[1])

        iu = np.triu_indices(6,k=1)

        assert_equal(cmat[iu], cmat[iu[1],iu[0]])
        assert_equal((np.arange(5)+1)**2, np.diag(cmat)[0:-1])

        expected = np.array([12, 21, 32, 45, 60, 88, 120, 156, 210, 300])
        iuu = np.triu_indices(5,k=1)
        assert_equal(expected, cmat[:-1,:-1][iuu])

        for i in range(5):
            assert_almost_equal(cmat[i,5], cmat[i,2]*17, 1)

        assert_almost_equal(cmat[5,5], 9*(17**2+18**2)+(16*18)**2, 1)

    def test_construct_covariance_matrix_nsources(self):
        """
        Check that the covariance matrix is constructed correctly from the inputs provided.
        """

        cvec = np.zeros((2,15))
        cvec[0] = np.arange(15)+1
        cvec[1] = -cvec[0]
        parallax = np.array([16, -16])
        vrad = np.array([17, -17])*auKmYearPerSec
        vrad_error = np.array([18, -18])*auKmYearPerSec

        cmat = construct_covariance_matrix(cvec, parallax, vrad, vrad_error)

        self.assertEquals(2, cmat.shape[0])
        self.assertEquals(6, cmat.shape[1])
        self.assertEquals(6, cmat.shape[2])

        iu = np.triu_indices(6,k=1)

        assert_equal(cmat[0,iu[0],iu[1]], cmat[0,iu[1],iu[0]])
        assert_equal((np.arange(5)+1)**2, np.diag(cmat[0])[0:-1])

        expected = np.array([12, 21, 32, 45, 60, 88, 120, 156, 210, 300])
        iuu = np.triu_indices(5,k=1)
        assert_equal(expected, cmat[0,:-1,:-1][iuu])

        for i in range(5):
            assert_almost_equal(cmat[0,i,5], cmat[0,i,2]*17, 1)

        assert_almost_equal(cmat[0,5,5], 9*(17**2+18**2)+(16*18)**2, 1)

        assert_equal(cmat[1,iu[0],iu[1]], cmat[1,iu[1],iu[0]])
        assert_equal((np.arange(5)+1)**2, np.diag(cmat[1])[0:-1])

        expected = -np.array([12, 21, 32, 45, 60, 88, 120, 156, 210, 300])
        iuu = np.triu_indices(5,k=1)
        assert_equal(expected, cmat[1,:-1,:-1][iuu])

        for i in range(5):
            assert_almost_equal(cmat[1,i,5], cmat[1,i,2]*(-17), 1)

        assert_almost_equal(cmat[1,5,5], 9*(17**2+18**2)+(16*18)**2, 1)
