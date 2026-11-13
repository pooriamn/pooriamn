# Experimental data pipeline

A small, dependency-free example of a repeatable experiment-data workflow: read a CSV, validate its schema and values, calculate a traceable time-weighted DC energy estimate and publish a JSON summary atomically.

```sh
python projects/experimental-pipeline/pipeline.py projects/experimental-pipeline/sample.csv summary.json
```

The input contains synthetic time (s), voltage (V) and current (A). Timestamps must strictly increase; measurements must be finite and non-negative. The energy integral uses trapezoidal interpolation between sample powers. No extrapolation or missing-value imputation is performed.

Output includes a SHA-256 digest of the exact source bytes. Rerunning with identical input yields identical JSON. A rejected input does not replace an existing report. This is a file-processing demonstration, not real-time instrument control.
