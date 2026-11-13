# Restricted diffusion: an upstream contribution candidate

The [impedance.py issue #269](https://github.com/ECSHackWeek/impedance.py/issues/269) asks for an anomalous restricted-diffusion element. It is an interesting extension of the existing open Warburg element, particularly for solid-state battery diffusion. This is a preparation note, not a submitted or accepted upstream patch.

## Model

Vicente, Haro and Garcia-Belmonte, *Chemical Communications* 54 (2018), 1025–1040, [DOI 10.1039/C7CC08373D](https://doi.org/10.1039/C7CC08373D), equation 5, give an impedance that can be expressed as

```
x = (j * 2 * pi * f * tau) ** (gamma / 2)
Z = Rd / (x * tanh(x))
```

Here Rd is in ohms, tau = 1/omega_d is in seconds and gamma is dimensionless. The ideal restricted-diffusion limit is gamma = 1; the paper discusses anomalous behaviour for gamma below 1. Positive frequency, positive Rd and tau, and 0 < gamma <= 1 are the intended physical domain.

A proposed upstream implementation would follow the existing `Wo` interface and use a vectorised complex power followed by `tanh`. The name, bounds and treatment of invalid inputs should follow the maintainers' conventions.

## Acceptance tests

- With gamma = 1, match the existing `Wo([Rd, tau], f)` over a logarithmic frequency grid.
- At high frequency, the phase tends to -gamma*pi/4 and the log-magnitude slope tends to -gamma/2.
- At low frequency, the leading term is Rd/(j*2*pi*f*tau)**gamma; the next real constant is Rd/3. The limiting phase tends to -gamma*pi/2.
- Test vector shape, finite positive frequencies and regression values independently of the implementation.
- Document the physical interpretation and parameter bounds; a good fit alone does not establish anomalous diffusion as the actual mechanism.

The next step is a fork-based contribution following the upstream project's conventions, with independent reference values and its full test suite. No issue or pull request has been posted upstream.
