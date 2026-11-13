"""Synthetic complex impedance and bounded grid fitting."""
from itertools import product
from math import isfinite, pi

def impedance(frequency_hz, rs, rct, capacitance):
    values = (frequency_hz, rs, rct, capacitance)
    if not all(isfinite(v) and v > 0 for v in values):
        raise ValueError("Frequency and circuit parameters must be finite and positive")
    return rs + rct / (1 + 1j * 2 * pi * frequency_hz * rct * capacitance)

def fit_grid(frequencies, measurements, rs_values, rct_values, c_values):
    """Return parameters and mean squared complex residual, on supplied grids."""
    frequencies, measurements = tuple(frequencies), tuple(measurements)
    if not frequencies or len(frequencies) != len(measurements):
        raise ValueError("Frequency and measurement arrays must be nonempty and aligned")
    if not all(isfinite(z.real) and isfinite(z.imag) for z in measurements):
        raise ValueError("Non-finite impedance")
    best = None
    for rs, rct, c in product(rs_values, rct_values, c_values):
        error = sum(abs(impedance(f, rs, rct, c) - z)**2
                    for f, z in zip(frequencies, measurements)) / len(frequencies)
        if best is None or error < best[0]:
            best = (error, (rs, rct, c))
    if best is None:
        raise ValueError("Parameter grids must be nonempty")
    return best[1], best[0]

if __name__ == "__main__":
    f = [10**(i/4) for i in range(-8, 21)]
    z = [impedance(x, 0.2, 1.5, 0.01) for x in f]
    parameters, error = fit_grid(f, z, [0.1, 0.2, 0.3], [1, 1.5, 2], [0.005, 0.01, 0.02])
    print("Rs, Rct, C:", parameters, "mean squared residual:", error)
