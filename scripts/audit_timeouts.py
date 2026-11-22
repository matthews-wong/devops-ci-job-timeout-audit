#!/usr/bin/env python3
"""Fail when a GitHub Actions job has no timeout-minutes, or one above a ceiling."""

import argparse
import sys
from pathlib import Path

import yaml

DEFAULT_MAX_MINUTES = 30
WORKFLOW_GLOBS = ("*.yml", "*.yaml")
WORKFLOW_DIR = Path(".github/workflows")


def audit_workflow(path, max_minutes):
    """Return one message per job in `path` that breaks the timeout policy."""
    try:
        doc = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        return [f"{path}: not valid YAML: {exc}"]
    jobs = doc.get("jobs") if isinstance(doc, dict) else None
    if not isinstance(jobs, dict):
        return [f"{path}: no jobs mapping found"]

    findings = []
    for name, job in jobs.items():
        if not isinstance(job, dict) or "uses" in job:
            # reusable-workflow callers cannot set timeout-minutes
            continue
        timeout = job.get("timeout-minutes")
        if timeout is None:
            findings.append(f"{path}: job '{name}' has no timeout-minutes")
        elif isinstance(timeout, str):
            continue  # an expression such as ${{ inputs.timeout }}
        elif isinstance(timeout, bool) or timeout <= 0 or timeout > max_minutes:
            findings.append(
                f"{path}: job '{name}' timeout-minutes is {timeout!r}, "
                f"expected 1..{max_minutes}"
            )
    return findings


def collect(paths):
    if paths:
        return [Path(p) for p in paths]
    return sorted(f for pattern in WORKFLOW_GLOBS for f in WORKFLOW_DIR.glob(pattern))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-minutes", type=int, default=DEFAULT_MAX_MINUTES)
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)

    files = collect(args.paths)
    if not files:
        print(f"no workflow files found under {WORKFLOW_DIR}", file=sys.stderr)
        return 1
    findings = [m for f in files for m in audit_workflow(f, args.max_minutes)]
    for message in findings:
        print(message)
    print(f"{len(files)} workflow(s) checked, {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
