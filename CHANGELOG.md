# Changelog

## 0.3.0

- Added independently integrated charge (Ah) and time-averaged current (A) to experimental CSV reports, while retaining existing report fields and validation rules.
- Applied the same calculation to the installable toolkit and standalone experimental example; added synthetic regression tests for uneven sampling, changing voltage and zero current.
- Clarified endpoint-trapezoid assumptions and the limits of missing-data interpretation. This release does not estimate Faradaic efficiency or gas production.

## 0.2.0

- Advanced EIS inverse modelling with analytic Jacobian, constrained multistart optimisation, RC/RQ comparison, AICc and local identifiability/uncertainty diagnostics.
- Dynamic electrolyser electrothermal model with Nernst pressure correction, apparent Butler–Volmer kinetics, Arrhenius ASR, energy-state integration and temperature-domain events.
- Reproducible synthetic computational studies and numerical verification; optional advanced dependencies.
- Introductory examples retained as quickstarts.

## 0.1.0

First versioned public toolkit.

- Shared installable Python package with impedance, stack, cycling throughput, polarisation and measurement-report modules.
- CLI for stack, impedance, signed-current integration and experimental reports.
- Browser workbench, documented synthetic examples and a public activity summary.
- Numerical regression tests, input validation tests and continuous integration on Python 3.10 and 3.12.

Known limits: idealised DC balances and simple equivalent circuits; no hardware control, general electrochemical simulation or production validation.
