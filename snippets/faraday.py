from math import isfinite

def hydrogen_kg_per_hour(current_a, cells=1, faradaic_efficiency=1.0):
    if not isinstance(cells,int) or isinstance(cells,bool) or cells<1:
        raise ValueError("Positive integer cell count required")
    if not isfinite(current_a) or current_a<0:
        raise ValueError("Nonnegative finite current required")
    if not isfinite(faradaic_efficiency) or not 0<=faradaic_efficiency<=1:
        raise ValueError("Efficiency must be between zero and one")
    return cells*current_a*faradaic_efficiency*3600*0.00201588/(2*96485.33212)
