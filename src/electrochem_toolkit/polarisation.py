"""Linear Tafel regression for a preselected, physically valid region."""
from math import isfinite, log10, sqrt

def tafel(current_density, overpotential_v):
    """Fit eta = a + b log10(j). j in A/cm², eta in V.

    Input must contain positive current magnitudes and signed overpotentials
    chosen consistently for one reaction branch. No automatic region selection.
    """
    j, eta = tuple(current_density), tuple(overpotential_v)
    if len(j) != len(eta) or len(j) < 3:
        raise ValueError("At least three aligned points are required")
    if not all(isfinite(x) and x > 0 for x in j) or not all(isfinite(x) for x in eta):
        raise ValueError("Use finite positive current magnitudes and finite potentials")
    x = [log10(v) for v in j]
    xm, ym = sum(x)/len(x), sum(eta)/len(eta)
    sxx = sum((v-xm)**2 for v in x)
    if sxx <= 0:
        raise ValueError("Current densities must span a nonzero log range")
    slope = sum((a-xm)*(b-ym) for a,b in zip(x,eta))/sxx
    intercept = ym-slope*xm
    rss = sum((b-intercept-slope*a)**2 for a,b in zip(x,eta))
    tss = sum((b-ym)**2 for b in eta)
    return {"slope_V_dec":slope,"intercept_V":intercept,
            "rmse_V":sqrt(rss/len(x)), "r_squared":1-rss/tss if tss else None}
