# Test the asymmetry calculators
# Derek Fujimoto
# Feb 2023

from bdata import bdata
from numpy.testing import *
import numpy as np
from bdata.asym_fns import *

# simple comparisons to hand calculations with base numbers
def test_get_simple():
    Fp = np.ones(10)
    Bp = np.ones(10)*2
    a = get_simple(Fp, Bp)
    assert all(a == -1/3)
    
def test_get_simple_err():
    Fp = np.ones(10)
    Bp = np.ones(10)*2
    da = get_simple_err(Fp, Bp)
    assert all(da == 2*np.sqrt(2/27))

def test_get_4counter():
    Fp = np.ones(10)
    Bp = np.ones(10)*2
    Fn = np.ones(10)*2
    Bn = np.ones(10)

    a = get_4counter(Fp, Fn, Bp, Bn)
    assert all(a == 1/3)
    
def test_get_4counter_err():
    Fp = np.ones(10)
    a = get_4counter_err(Fp, Fp, Fp, Fp)
    assert all(a == 1/2)

def test_get_alpha():
    Fp = np.ones(10)
    Bp = np.ones(10)*2

    f = [Fp]*4
    b = [Bp]*4

    a = get_alpha(f, b)
    assert all(a == 1/4)
    
def test_get_alpha_err():
    Fp = np.ones(10)
    Bp = np.ones(10)*2

    f = [Fp]*4
    b = [Bp]*4

    a = get_alpha_err(f, b)
    
def test_asym_rebin():
    """
        Check that the rebinning works
    """

    dat = bdata(40123, 2021)
    
    # rebin 1
    dat.asym('c', rebin=1)

    # rebin 2
    dat.asym('c', rebin=2)

    # rebin 10
    dat.asym('c', rebin=10)

    # rebin 20
    dat.asym('c', rebin=20)

# compare background subtraction to no backgrouns subtraction (background zero)
def test_get_4counter_err_bkgd_zero():
    n_prebeam = 2
    x = np.ones(12)
    x[:n_prebeam] = 0

    a = get_4counter_err_bkgd(x, x, x, x, n_prebeam)

    x = x[n_prebeam:]
    a2 = get_4counter_err(x, x, x, x)

    assert_array_equal(a[n_prebeam:], a2, err_msg="Background subtraction unequal 4counter err")
    
def test_get_simple_err_bkgd_zero():
    n_prebeam = 2
    x = np.ones(12)
    x[:n_prebeam] = 0

    a = get_simple_err_bkgd(x, x, n_prebeam)

    x = x[n_prebeam:]
    a2 = get_simple_err(x, x)

    assert_array_equal(a[n_prebeam:], a2, err_msg="Background subtraction unequal simple err")

def test_get_alpha_err_bkgd_zero():
    n_prebeam = 2
    x = np.ones(12)
    x[:n_prebeam] = 0

    inpt = np.array([x, x, x, x])
    a = get_alpha_err_bkgd(inpt, inpt, n_prebeam)

    x = x[n_prebeam:]
    inpt = np.array([x, x, x, x])
    a2 = get_alpha_err(inpt, inpt)

    assert_array_equal(a[n_prebeam:], a2, err_msg="Background subtraction unequal alpha err")

