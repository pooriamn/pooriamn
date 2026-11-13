# Electrochemical Engineering Toolkit

A small Python package for calculations and data processing I encounter in electrochemical engineering. The idea is to keep the scientific core separate from the interface, so the same functions can be used in a script, a dashboard or an automated workflow.

## Install and run

Python 3.10 or later. From the repository root:

```sh
python -m pip install .
electrochem-toolkit stack --cells 10 --area 100 --density 0.3 --voltage 1.8
electrochem-toolkit impedance --frequency 10 --rs 0.2 --rct 1.5 --capacitance 0.01
electrochem-toolkit battery --time 0 3600 7200 --current 2 2 -2
electrochem-toolkit report projects/experimental-pipeline/sample.csv summary.json
```

Or use the Python interfaces directly:

```python
from electrochem_toolkit.stack import calculate
from electrochem_toolkit.impedance import impedance, bode, fit_grid
from electrochem_toolkit.battery import throughput
from electrochem_toolkit.polarisation import tafel

result = calculate(10, 100, 0.3, 1.8)
print(result["dc_specific_energy_kWh_kg"])
```

| Module | Purpose |
| --- | --- |
| impedance | Series-R/parallel-RC response, complex grid fitting, Bode magnitude and phase |
| stack | DC stack balance, Faradaic hydrogen production, specific energy |
| battery | Signed-current charge/discharge throughput, zero-crossing integration |
| polarisation | Linear Tafel regression for a manually selected valid region |
| pipeline | Validated CSV processing, energy integration, atomic JSON reports |

## Design and validation

The calculation layer uses only the Python standard library. Inputs are explicitly validated, units are documented and the examples use synthetic data. Run `python -m unittest discover -s tests -v` after installation. See the [development notes](../journal/README.md) for the reasoning behind several design choices.

The [browser workbench](../docs/toolkit.html) provides independent JavaScript demonstrations of the same equations; it does not call the Python package or an external service.

## Scope

Version 0.1.0 is an initial educational release. This is not a general EIS fitting package, a battery state estimator, an electrolyser design model or a control system. Tafel region selection and measurement validity remain the user's responsibility. No private company code or data are included. For scientific or engineering sign-off, validate the model against independent reference data and the intended operating conditions.
