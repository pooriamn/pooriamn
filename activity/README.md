# Public development activity

The profile summary reports the activity of this repository only. It is not a measure of my total GitHub work, and does not query or expose private repositories.

The [generator](../scripts/public_activity.py) reads only this repository's public GitHub REST API, checks that the repository is explicitly public, and counts open issues (excluding PRs), merged pull requests and stable published releases. On GitHub Actions, it uses the job's short-lived `GITHUB_TOKEN` to avoid the anonymous API rate limit; it can still run without a token locally. The latest stable version is shown separately. No issue titles, private names, user-level contribution data or personal information are collected.

[Current snapshot](snapshot.json) · [Automation workflow](../.github/workflows/public-activity.yml)

The workflow refreshes on relevant events and on a weekly schedule. The token is used only to query this public repository, not to enumerate private repositories or account-wide activity. It commits the generated files only when the counts or version change. A failed API read or invalid response stops the job before publication; the previous snapshot is retained.

For account-wide activity, see the [native GitHub contribution calendar](https://github.com/pooriamn).
