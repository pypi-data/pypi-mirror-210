# Test bdata asymmetry calculators
# Derek Fujimoto
# Feb 2023

import numpy as np
from numpy.testing import *
from bdata import bdata

### SLR TESTS NO BACKGROUND CORRECTIONS ###

# test data to set some of the settings right: SLR Li8
bdat = bdata(40123, 2021)
bdat.slr_bkgd_corr = False
bdat.slr_rm_prebeam = False

def test_get_asym_bck():

    fn = bdata._get_asym_bck

    F = np.ones(10)
    B = np.ones(10)
    a, da = fn(bdat, [None, None, F, B])
    
    assert all(a == 0), 'SLR bck'
    assert all(da == 2*np.sqrt(1/8)), 'SLR bck err'

def test_get_asym_fwd():

    fn = bdata._get_asym_fwd

    F = np.ones(10)
    B = np.ones(10)
    a, da = fn(bdat, [F, B, None, None])

    assert all(a == 0), 'SLR fwd'
    assert all(da == 2*np.sqrt(1/8)), 'SLR fwd err'

def test_get_asym_pos():

    fn = bdata._get_asym_pos

    F = np.ones(10)
    B = np.ones(10)
    a, da = fn(bdat, [F, None, B, None])

    assert all(a == 0), 'SLR pos'
    assert all(da == 2*np.sqrt(1/8)), 'SLR pos err'

def test_get_asym_neg():

    fn = bdata._get_asym_neg

    F = np.ones(10)
    B = np.ones(10)
    a, da = fn(bdat, [None, F, None, B])

    assert all(a == 0), 'SLR neg'
    assert all(da == 2*np.sqrt(1/8)), 'SLR neg err'
    
def test_get_asym_alpha():

    fn = bdata._get_asym_alpha

    F = np.ones(10)
    B = np.ones(10)*2

    inptF = np.array([F]*4)
    inptB = np.array([B]*4)
    a, da = fn(bdat, inptF, inptB)

    assert all(a == 1/4), 'SLR alpha'