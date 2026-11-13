# A report should survive a bad input file

The useful part of automating an experiment is not just generating a report faster. It is being able to trust what happens on the second, hundredth or failed run.

The public CSV example checks the schema and numerical values before writing anything. It rejects repeated timestamps, missing values and non-finite measurements instead of guessing what the input meant. The output carries a hash of the source bytes, and it is written to a temporary file before replacing the previous report.

The important test is not just whether a valid file produces a result. It is whether an invalid file leaves the last good result intact.

[Example](../projects/experimental-pipeline/README.md)
