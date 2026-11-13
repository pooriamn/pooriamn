# Run the examples

The three projects here are small enough to read in one sitting. Each solves a different part of a typical engineering workflow, from interpreting impedance data to calculating stack performance or processing a measurement file.

| Example | Start here |
| --- | --- |
| Electrochemical analysis | [Model, assumptions and command](electrochemical-analysis/README.md) |
| Electrolyser calculator | [Inputs, equations and outputs](electrolyser-calculator/README.md) |
| Experimental data pipeline | [Sample data and reporting workflow](experimental-pipeline/README.md) |

All three run on Python 3.10 or newer using only the standard library.

From the repository root, run the tests with:

```sh
python -m unittest discover -s tests -v
```

The same suite runs in [GitHub Actions](https://github.com/pooriamn/pooriamn/actions/workflows/verify.yml).

These are educational examples, not production software. They use synthetic inputs and are not intended for equipment control, safety limits or engineering sign-off.
