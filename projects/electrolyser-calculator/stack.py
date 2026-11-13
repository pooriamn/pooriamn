"""Idealised DC balance for a series-connected electrolyser stack."""
import argparse
import json
from math import isfinite

FARADAY = 96485.33212
H2_KG_PER_MOL = 0.00201588

def calculate(cells, area_cm2, current_density, cell_voltage, efficiency=1.0):
    if not isinstance(cells, int) or isinstance(cells, bool) or cells < 1:
        raise ValueError("cells must be a positive integer")
    if not all(isfinite(v) and v > 0 for v in (area_cm2, current_density, cell_voltage)):
        raise ValueError("Area, current density and voltage must be finite and positive")
    if not isfinite(efficiency) or not 0 < efficiency <= 1:
        raise ValueError("Faradaic efficiency must be in (0, 1]")
    current = area_cm2 * current_density
    voltage = cells * cell_voltage
    power_kw = current * voltage / 1000
    hydrogen_kg_h = cells * current * efficiency * 3600 * H2_KG_PER_MOL / (2 * FARADAY)
    return {"current_A": current, "stack_voltage_V": voltage,
            "dc_power_kW": power_kw, "hydrogen_kg_h": hydrogen_kg_h,
            "dc_specific_energy_kWh_kg": power_kw / hydrogen_kg_h}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cells", type=int, required=True)
    parser.add_argument("--area", type=float, required=True)
    parser.add_argument("--current-density", type=float, required=True)
    parser.add_argument("--voltage", type=float, required=True)
    parser.add_argument("--efficiency", type=float, default=1.0)
    args = parser.parse_args()
    print(json.dumps(calculate(args.cells, args.area, args.current_density,
                               args.voltage, args.efficiency), indent=2))
