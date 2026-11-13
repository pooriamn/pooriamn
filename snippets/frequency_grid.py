from math import isfinite, log10

def frequency_grid(high_hz, low_hz, points_per_decade=10):
    if not (isfinite(high_hz) and isfinite(low_hz) and high_hz >= low_hz > 0):
        raise ValueError("Require finite high >= low > 0")
    if not isinstance(points_per_decade,int) or points_per_decade < 1:
        raise ValueError("Positive integer points_per_decade required")
    from math import ceil
    intervals=max(1,ceil((log10(high_hz)-log10(low_hz))*points_per_decade))
    if high_hz == low_hz:
        return [high_hz]
    return [10**(log10(high_hz)+(log10(low_hz)-log10(high_hz))*i/intervals)
            for i in range(intervals+1)]
