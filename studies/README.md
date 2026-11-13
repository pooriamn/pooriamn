# Selected computational studies

The examples here are larger than the introductory toolkit demonstrations. They focus on two questions that are central to electrochemical engineering: whether an impedance model is supported by the data, and how electrical and thermal behaviour interact in a stack under changing load.

| Study | Methods |
| --- | --- |
| [Electrochemical inverse modelling](eis-inverse/README.md) | Complex nonlinear least squares, analytic Jacobian, multistart, AICc and local uncertainty |
| [Dynamic electrolyser electrothermal model](electrothermal-stack/README.md) | Thermodynamics, apparent Butler–Volmer kinetics, temperature-dependent resistance, ODE integration and energy balance |

Run from the repository root with Python 3.10 or newer:

```sh
python -m pip install ".[advanced]"
python studies/eis-inverse/run.py
python studies/electrothermal-stack/run.py
python -m unittest discover -s tests -v
```

The data and parameters are synthetic, and all assumptions are documented. These are computational studies, not validated models of a commercial stack or a substitute for measurement validity checks.
