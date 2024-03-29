'''
Copyright (C) 2019 The Crown (i.e. Her Majesty the Queen in Right of Canada)

This file is an add-on to RAVE.

RAVE is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

RAVE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with RAVE.  If not, see <http://www.gnu.org/licenses/>.
------------------------------------------------------------------------*/

ncarb unit tests

@file
@author Daniel Michelson, Environment and Climate Change Cananda
@date 2019-11-19
'''
import os, unittest
import _rave
import _raveio
import _ncarb
import ncarb
import numpy as np


class ncarbTest(unittest.TestCase):
    THRESHOLDS = '../../config/pid_thresholds.nexrad'
    FIXTURE = '../CASBV_201907302000_0.4.h5'
    REF_FIXTURE = '../CASBV_201907302000_0.4_ref.h5'
    PROFILE = '../2019073000_CASBV.prof.txt'
    REF_TEMPC = '../profile_0.4.npy'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_interpolateProfile(self):
        reference = np.array([15.,  17.5,  5.,  -2.5, -7.5])
        height = np.array([0.0, 100.0, 200.0, 300.0])
        tempc = np.array([20.0, 10.0, 0.0, -10.0])
        myheight = np.array([50.0, 25.0, 150.0, 225.0, 275.0])
        out = ncarb.interpolateProfile(height, tempc, myheight)
        self.assertEqual(out.all(), reference.all())

    def test_interpolateRealProfile(self):
        profile = ncarb.readProfile(self.PROFILE, scale_height=1000)
        reference = np.load(self.REF_TEMPC)
        scan = _raveio.open(self.FIXTURE).object
        rtempc = ncarb.getTempcProfile(scan, profile)
        self.assertEqual(rtempc.all(), reference.all())

    def test_generateNcar_pid(self):
        rio = _raveio.open(self.FIXTURE)
        scan = rio.object
        profile = ncarb.readProfile(self.PROFILE, scale_height=1000)
        ncarb.THRESHOLDS_FILE['nexrad'] = self.THRESHOLDS
        ncarb.pidScan(scan, profile, median_filter_len=7,
                      pid_thresholds='nexrad', keepExtras=True)
        rio.object = scan
        ref = _raveio.open(self.REF_FIXTURE).object
        self.assertFalse(different(scan, ref))
        self.assertFalse(different(scan, ref, "CLASS2"))
        #rio.save(self.REF_FIXTURE)


# Helper function to determine whether two parameter arrays differ
def different(scan1, scan2, param="CLASS"):
    a = scan1.getParameter(param).getData()
    b = scan2.getParameter(param).getData()
    c = a == b
    d = np.sum(np.where(np.equal(c, False), 1, 0).flat)
    if d > 0:
        return True
    else:
        return False 
