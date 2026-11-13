# Electrolyser engineering calculator

An idealised DC stack balance for series-connected electrolysis cells. Uses Faraday's law with a user-supplied Faradaic efficiency. Reports current, stack voltage, DC power, hydrogen production rate and DC specific energy.

![Series stack electrical balance](stack-balance.svg)

```sh
python projects/electrolyser-calculator/stack.py --cells 10 --area 100 --current-density 0.3 --voltage 1.8
```

Area is in cm² per cell; current density is A/cm²; voltage is V per cell. The hydrogen molar mass is 2.01588 g/mol and the Faraday constant is 96485.33212 C/mol. Two electrons are required per hydrogen molecule.

This is a steady-state electrical balance, not a predictive voltage model. It excludes auxiliaries, AC conversion losses, pressure, heat transfer, crossover and gas purity. No equipment limits or safety claims are implied.

See [source](stack.py).
