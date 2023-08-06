# Low level asymmetry calculators for bdata
# Derek Fujimoto
# Feb 2023

import numpy as np

# ======================================================================= #
def get_4counter(Fp, Fn, Bp, Bn):
    """
    Find the combined asymmetry. Elegant 4-counter method.
    Inputs are counter np.arrays
    """

    # pre-calcs
    r_denom = Fp*Bn
    r_denom[r_denom==0] = np.nan
    r = np.sqrt((Bp*Fn/r_denom))
    r[r==-1] = np.nan

    # combined asymmetry
    asym_comb = (r-1)/(r+1)
    
    # replace nan with zero 
    asym_comb[np.isnan(asym_comb)] = 0.
    
    return asym_comb

# =======================================================================
def get_4counter_err(Fp, Fn, Bp, Bn):
    """
    Find the combined asymmetry error. Elegant 4-counter method.
    Inputs are counter np.arrays
    """

    # pre-calcs
    r_denom = Fp*Bn
    r_denom[r_denom==0] = np.nan
    r = np.sqrt((Bp*Fn/r_denom))
    r[r==-1] = np.nan

    # check for div by zero
    Fp[Fp==0] = np.nan                  
    Bp[Bp==0] = np.nan
    Fn[Fn==0] = np.nan
    Bn[Bn==0] = np.nan
    
    # error in combined asymmetry
    asym_comb_err = r*np.sqrt(1/Bp + 1/Fp + 1/Bn + 1/Fn)/np.square(r+1)
    
    # replace nan with zero 
    asym_comb_err[np.isnan(asym_comb_err)] = 0.
    
    return asym_comb_err

# =======================================================================
def get_4counter_err_bkgd(Fp, Fn, Bp, Bn, n_prebeam):
    """
    Find the combined asymmetry error in the case of background corrections. 
    Elegant 4-counter method.

    Inputs are counter np.arrays, uncorrected, and the number of prebeam bins
    """

    # convert input to list
    d = [Fp, Fn, Bp, Bn]

    # get background correction means and variance in the mean
    d_bkmean = [np.mean(di[:n_prebeam]) for di in d]
    d_bkvar  = [np.var(di[:n_prebeam])/n_prebeam for di in d]

    # get variances in these new histograms: combine poisson and gaussian variances
    d_var = [d[i] + d_bkvar[i] for i in range(len(d))]

    # correct histograms using background mean
    d = [d[i]-d_bkmean[i] for i in range(len(d))]
    
    # remove negative count values and check for div by zero
    for i in range(len(d)):
        d[i][d[i]<=0] = np.nan

    # re-expand to human-readable variables
    Fp, Fn, Bp, Bn = d
    vFp, vFn, vBp, vBn = d_var

    # calculate r
    r_denom = Fp*Bn
    r_denom[r_denom==0] = np.nan
    r = np.sqrt((Bp*Fn/r_denom))
    r[r==-1] = np.nan
    
    # error in r
    r_err = 0.5*np.sqrt(vFn*(Bp/(Fp*Fn*Bn)) +
                        vBp*(Fn/(Fp*Bp*Bn)) +
                        vFp*(Fn*Bp/(Bn*Fp**3)) +
                        vBn*(Fn*Bp/(Fp*Bn**3)))

    # error in asymmetry
    asym_comb_err = r_err * 2/(r+1)**2

    # replace nan with zero 
    asym_comb_err[np.isnan(asym_comb_err)] = 0.
    
    return asym_comb_err

# ======================================================================= #
def get_simple(F, B):
    """
        Do the simple asymmetry calculation: F-B / F+B
        Inputs are counter np.arrays
    """
    
    # pre-calcs
    denom = F+B
    
    # check for div by zero
    denom[denom==0] = np.nan          
    
    # asymmetries
    asym = (F-B)/denom
                
    # remove nan            
    asym[np.isnan(asym)] = 0.
        
    return asym

# ======================================================================= #
def get_simple_err(F, B):
    """
        Get the error of the simple asymmetry calculation (F-B / F+B)
        Inputs are counter np.arrays
    """
    
    # pre-calcs
    denom = F+B
    
    # check for div by zero
    denom[denom==0] = np.nan          
    
    # errors 
    # https://www.wolframalpha.com/input/?i=%E2%88%9A(F*(derivative+of+((F-B)%2F(F%2BB))+with+respect+to+F)%5E2+%2B+B*(derivative+of+((F-B)%2F(F%2BB))+with+respect+to+B)%5E2)
    asym_err = 2*np.sqrt(F*B/np.power(denom, 3))
    
    # remove nan            
    asym_err[np.isnan(asym_err)] = 0.
        
    return asym_err
    
# ======================================================================= #
def get_simple_err_bkgd(F, B, n_prebeam):
    """
        Get the error of the simple asymmetry calculation (F-B / F+B) in the case of background corrections.
        Inputs are counter np.arrays, uncorrected, and the number of prebeam bins
    """
    
    # convert input to list
    d = [F, B]

    # get background correction means and variance in the mean
    d_bkmean = [np.mean(di[:n_prebeam]) for di in d]
    d_bkvar  = [np.var(di[:n_prebeam])/n_prebeam for di in d]

    # get variances in these new histograms: combine poisson and gaussian variances
    d_var = [d[i] + d_bkvar[i] for i in range(len(d))]

    # correct histograms using background mean
    d = [d[i]-d_bkmean[i] for i in range(len(d))]
    
    # remove negative count values and check for div by zero
    for i in range(len(d)):
        d[i][d[i]<=0] = np.nan

    # re-expand to human-readable variables
    F, B = d
    vF, vB = d_var

    # pre-calcs
    denom = F+B
    
    # check for div by zero
    denom[denom==0] = np.nan          
    
    # errors 
    asym_err = 2 * np.sqrt( vF*(B/(F+B)**2)**2 + vB*(F/(F+B)**2)**2)
    
    # remove nan            
    asym_err[np.isnan(asym_err)] = 0.
        
    return asym_err

# ======================================================================= #
def get_alpha(a, b):
    """
        Find alpha diffusion ratios from cryo oven with alpha detectors. 
        a: list of alpha detector histograms (each helicity)
        b: list of beta  detector histograms (each helicity)
        
        a/b = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
    """
    
    # just  use AL0
    try:
        a = a[2:4]
    except IndexError:
        a = a[:2]
        
    # sum counts in alpha detectors
    asum = np.sum(a, axis=0)
    
    # sum counts in beta detectors
    bsum = np.sum(b, axis=0)
    
    # check for dividing by zero 
    bsum[bsum == 0] = np.nan
    
    # asym calcs
    asym = asum/bsum

    return asym

# ======================================================================= #
def get_alpha_err(a, b):
    """
        Find alpha diffusion ratio error from cryo oven with alpha detectors. 
        a: list of alpha detector histograms (each helicity)
        b: list of beta  detector histograms (each helicity)
        
        a/b = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
    """
    
    # just  use AL0
    try:
        a = a[2:4]
    except IndexError:
        a = a[:2]
        
    # sum counts in alpha detectors
    asum = np.sum(a, axis=0)
    
    # sum counts in beta detectors
    bsum = np.sum(b, axis=0)
    
    # check for dividing by zero 
    asum[asum == 0] = np.nan
    bsum[bsum == 0] = np.nan
    
    # errors
    asym = asum/bsum
    dasym = asym*np.sqrt(1/asum + 1/bsum)
    
    return dasym
    
# ======================================================================= #
def get_alpha_err_bkgd(a, b, n_prebeam):
    """
        Find alpha diffusion ratio error from cryo oven with alpha detectors, 
        including background subtraction
        a: list of alpha detector histograms (each helicity)
        b: list of beta  detector histograms (each helicity)
        
        a/b = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
    """
    
    # just  use AL0
    try:
        a = a[2:4]
    except IndexError:
        a = a[:2]
        
    # sum counts in alpha detectors
    asum = np.sum(a, axis=0)
    
    # sum counts in beta detectors
    bsum = np.sum(b, axis=0)
    
    # background variances
    avar = np.var(asum[:n_prebeam])
    bvar = np.var(bsum[:n_prebeam])
    
    # variances in sums
    asum_var = avar + asum
    bsum_var = bvar + bsum

    # background correction
    asum -= np.mean(asum[:n_prebeam])
    bsum -= np.mean(bsum[:n_prebeam])

    # check for dividing by zero 
    asum[asum == 0] = np.nan
    bsum[bsum == 0] = np.nan
    
    # errors
    asym = asum/bsum
    dasym = asym*np.sqrt(asum_var/asum**2 + bsum_var/bsum**2)
    
    return dasym