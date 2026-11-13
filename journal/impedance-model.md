# Starting with a simple impedance model

I tend to start with the smallest model that explains the part of a spectrum I am interested in. For the synthetic example here, a series resistance and a parallel RC element are enough. The high-frequency intercept approaches the series resistance, the low-frequency intercept approaches the sum of the two resistances, and the arc reaches its maximum at 1/(2πRC).

That gives several independent checks before looking at a fit residual. The grid search in the example is deliberately transparent: the known parameters are on the grid, so the numerical test checks exact recovery. That is not a claim about fitting noisy or real experimental data.

In a more realistic fitting tool I would want residuals by frequency, parameter bounds, uncertainty estimates and a clear indication when parameters are poorly identified. A convincing fit is not the same thing as a convincing physical model.

[Example](../projects/electrochemical-analysis/README.md)
