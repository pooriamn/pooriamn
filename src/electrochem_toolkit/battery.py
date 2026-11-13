"""Battery throughput from signed current and increasing timestamps.

Positive current = charge, negative = discharge. Current is linearly
interpolated between samples; a sign change is split at its zero crossing.
"""
from math import isfinite

def throughput(time_s, current_a):
    t, i = tuple(time_s), tuple(current_a)
    if len(t) != len(i) or len(t) < 2:
        raise ValueError("At least two aligned samples are required")
    if not all(isfinite(x) for x in (*t, *i)):
        raise ValueError("Samples must be finite")
    charge = discharge = 0.0
    for a, b, u, v in zip(t, t[1:], i, i[1:]):
        dt = b-a
        if dt <= 0:
            raise ValueError("Timestamps must strictly increase")
        if u*v < 0:
            fraction = abs(u)/(abs(u)+abs(v))
            first = u*dt*fraction/2
            second = v*dt*(1-fraction)/2
            charge += max(first,0)+max(second,0)
            discharge += -min(first,0)-min(second,0)
        else:
            q = dt*(u+v)/2
            charge += max(q,0)
            discharge += -min(q,0)
    if not all(isfinite(x) for x in (charge, discharge)):
        raise ValueError("Charge integration overflow")
    return {"charge_Ah":charge/3600, "discharge_Ah":discharge/3600,
            "net_Ah":(charge-discharge)/3600}
