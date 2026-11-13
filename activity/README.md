# Public development activity

The profile summary reports the activity of this repository only. It is not a measure of my total GitHub work, and does not query or expose private repositories.

The [generator](../scripts/public_activity.py) reads the public GitHub REST API without credentials, checks the repository is public, and counts open issues (excluding PRs), merged pull requests and stable published releases. The latest stable version is shown separately. No issue titles, private names, user-level contribution data or personal information are collected.

[Current snapshot](snapshot.json) · [Automation workflow](../.github/workflows/public-activity.yml)

The workflow refreshes on relevant events and on a weekly schedule. It commits the generated files only when the counts or version change. A failed API read or invalid response stops the job before publication; the previous snapshot is retained.

For account-wide activity, see the [native GitHub contribution calendar](https://github.com/pooriamn).
