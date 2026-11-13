# Electrochemical analysis toolkit

A minimal Python demonstration of fitting a series resistance and a parallel charge-transfer resistance / capacitance element to complex impedance data.

The model is Z = Rs + Rct / (1 + j 2πf Rct C). All resistances are in ohms, capacitance is in farads and frequency is in hertz. The example generates noise-free synthetic measurements and performs a bounded grid search using complex least squares. It is intentionally small and dependency-free.

```sh
python projects/electrochemical-analysis/impedance.py
```

The example reports the best parameter combination and residual. A fit does not establish that the circuit is physically unique. The model omits diffusion, inductance, distributed capacitance and non-stationarity; real measurements require independent validation, residual analysis and uncertainty assessment.

See [source](impedance.py) and [tests](../../tests/test_demos.py).
