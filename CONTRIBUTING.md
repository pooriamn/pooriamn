# Contributing

Start with a reproducible problem or a specific improvement. For numerical changes, include units, assumptions and an independent expected result. Use synthetic or openly licensed input data; never submit company data, credentials or unpublished research.

1. Open an issue explaining the problem and acceptance criteria.
2. Create a branch and make the smallest useful change.
3. Install the package and run the tests.
4. Open a pull request describing the change, its limits and how it was checked.

For a bug report, include the Python version, command, input and observed versus expected result. A good failure case is worth more than a long description without a reproducer.

```sh
python -m pip install .
python -m unittest discover -s tests -v
```

Code is MIT-licensed. Profile text, personal branding and photographs are not included in the software licence. Do not reuse personal identity or branding to imply endorsement.
