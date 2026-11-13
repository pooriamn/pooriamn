# Keeping the calculation layer separate from the interface

A scientific calculation often starts as a script. When the same calculation is needed in a second workflow, the temptation is to copy it and change a few lines. That creates two versions of the method to maintain.

The toolkit keeps numerical functions in an importable package, with a thin command-line layer. Tests exercise the calculation functions directly. A separate browser example demonstrates the same physical equations, but it does not pretend to use the Python implementation.

The next step would be to add more representative reference datasets and assess uncertainty, rather than simply adding more interfaces. A clean architecture is only useful if the calculation itself is sound.

[Toolkit](../toolkit/README.md)
