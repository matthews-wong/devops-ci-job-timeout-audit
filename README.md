# devops-ci-job-timeout-audit

A job without `timeout-minutes` runs for six hours when a step hangs, and
bills every minute of it. This repo is a small audit that fails when a
GitHub Actions job has no timeout, or one above a ceiling you choose.

## Usage

    python3 scripts/audit_timeouts.py [--max-minutes 30] [path ...]

With no paths it scans `.github/workflows/*.yml` and `*.yaml`. Exit code is
`1` when any job is flagged, `0` otherwise.

Jobs that call a reusable workflow (`uses:`) are skipped: GitHub does not
allow `timeout-minutes` on them, the called workflow owns it. Expression
values such as `${{ inputs.timeout }}` are accepted as-is.

## Validate

    pip install -r requirements.txt
    make validate

`make validate` runs the unit tests, `actionlint` (install it separately;
CI skips it rather than pipe an installer into a shell) and the audit
against this repository's own workflows.
