"""Read a repository's issue-dependency graph back from GitHub and print its waves.

    python seed/tools/waves_from_github.py --repo perro-ruidoso/flashcards-seed
    python seed/tools/waves_from_github.py --repo OWNER/REPO --mermaid
    python seed/tools/waves_from_github.py --repo OWNER/REPO --label ready-for-agent

Reads every open issue's `blockedBy` relation with `gh issue list --json` (gh >= 2.94.0),
runs Kahn's algorithm on the result, and prints one line per wave: the tickets that
could each be handed to a concurrent agent session once the previous wave has landed.
`--mermaid` prints the graph as a Mermaid `graph LR` block instead.

Issues that have sub-issues (a spec issue whose tickets are its children) are parents,
not tickets, and are skipped unless `--include-parents` is given. `--label` narrows the
set further. GitHub does not reject a dependency cycle - verified 2026-09-13 - so a cycle
is reported here rather than assumed impossible.

This derives the graph from what GitHub stores, not from `backlog.py`, so it is the
check that the filed edges match the spec - and the M11 exercise students run on their
own Instance.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def fetch(repo: str, labels: list[str], include_parents: bool) -> list[dict]:
    cmd = ["gh", "issue", "list", "-R", repo, "--state", "open", "--limit", "200",
           "--json", "number,title,blockedBy,subIssuesSummary"]
    for label in labels:
        cmd += ["--label", label]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    issues = json.loads(out)
    if not include_parents:
        issues = [i for i in issues if i["subIssuesSummary"]["total"] == 0]
    return issues


def waves(issues: list[dict]) -> list[list[int]]:
    blockers = {i["number"]: {b["number"] for b in i["blockedBy"]["nodes"]} for i in issues}
    known = set(blockers)
    remaining = {n: {b for b in bs if b in known} for n, bs in blockers.items()}
    result: list[list[int]] = []
    while remaining:
        ready = sorted(n for n, bs in remaining.items() if not bs)
        if not ready:
            raise SystemExit(f"cycle among {sorted(remaining)}")
        result.append(ready)
        for n in ready:
            del remaining[n]
        for bs in remaining.values():
            bs.difference_update(ready)
    return result


def mermaid(issues: list[dict]) -> str:
    lines = ["graph LR"]
    for i in sorted(issues, key=lambda x: x["number"]):
        lines.append(f'  I{i["number"]}["#{i["number"]} {i["title"]}"]')
    for i in sorted(issues, key=lambda x: x["number"]):
        for b in i["blockedBy"]["nodes"]:
            lines.append(f"  I{b['number']} --> I{i['number']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="OWNER/REPO")
    ap.add_argument("--mermaid", action="store_true", help="print a Mermaid graph instead")
    ap.add_argument("--label", action="append", default=[], help="only issues with this label (repeatable)")
    ap.add_argument("--include-parents", action="store_true",
                    help="keep issues that have sub-issues (skipped by default)")
    args = ap.parse_args(argv)

    issues = fetch(args.repo, args.label, args.include_parents)
    if not issues:
        print("no matching open issues")
        return 1
    if args.mermaid:
        print(mermaid(issues))
        return 0

    edges = sum(i["blockedBy"]["totalCount"] for i in issues)
    joins = sorted(i["number"] for i in issues if i["blockedBy"]["totalCount"] >= 2)
    ws = waves(issues)
    print(f"{len(issues)} issues, {edges} blocking edges, "
          f"{len(joins)} joins (2+ blockers): {', '.join(f'#{n}' for n in joins)}")
    for k, w in enumerate(ws, start=1):
        print(f"wave {k}  " + "  ".join(f"#{n}" for n in w))
    print(f"{len(ws)} waves, max parallel width {max(len(w) for w in ws)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
