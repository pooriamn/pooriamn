# Technical demonstrations

Three independent, educational examples using synthetic inputs and standard equations. No company code, experimental records or confidential data are included.

- [Electrochemical analysis](electrochemical-analysis/README.md)
- [Electrolyser calculator](electrolyser-calculator/README.md)
- [Experimental pipeline](experimental-pipeline/README.md)

## Run the verification suite

Python 3.10 or newer; no external dependencies.

```sh
python -m unittest discover -s tests -v
```

Run from the repository root. Each project has a separate command-line entry point and documented assumptions. These demonstrations are not validated production tools, and must not be used to control equipment or establish safety limits.
