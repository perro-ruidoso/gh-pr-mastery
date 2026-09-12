"""File the 15-ticket backlog from seed/SPEC.md section 6 into a GitHub repo.

    python file_backlog.py --repo perro-ruidoso/flashcards-seed [--dry-run]

Creates each issue in topological order, then records every blocking edge as a real
GitHub issue dependency:

    POST /repos/{owner}/{repo}/issues/{n}/dependencies/blocked_by  {"issue_id": <db id>}

verified against the live API on 2026-09-12. Idempotent: an issue whose exact title
already exists is reused rather than duplicated, and a dependency that already exists is
left alone, so a partial run can simply be re-run.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

import backlog

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


class GhError(RuntimeError):
    pass


def gh(*args: str) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise GhError((proc.stderr or proc.stdout).strip())
    return proc.stdout


def existing_issues(repo: str) -> dict[str, int]:
    """Map issue title -> number, for every open or closed issue in the repo."""
    raw = gh(
        "issue", "list", "--repo", repo, "--state", "all", "--limit", "200",
        "--json", "number,title",
    )
    return {row["title"]: row["number"] for row in json.loads(raw or "[]")}


def create_issue(repo: str, title: str, body: str) -> int:
    url = gh("issue", "create", "--repo", repo, "--title", title, "--body", body).strip()
    return int(url.rstrip("/").rsplit("/", 1)[-1])


def issue_db_id(repo: str, number: int) -> int:
    return int(gh("api", f"repos/{repo}/issues/{number}", "--jq", ".id").strip())


def blocked_by(repo: str, number: int) -> set[int]:
    raw = gh("api", f"repos/{repo}/issues/{number}/dependencies/blocked_by")
    return {row["number"] for row in json.loads(raw or "[]")}


def add_blocked_by(repo: str, number: int, blocker_db_id: int) -> None:
    gh(
        "api", "-X", "POST",
        f"repos/{repo}/issues/{number}/dependencies/blocked_by",
        "-F", f"issue_id={blocker_db_id}",
        "--silent",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, help="OWNER/NAME")
    parser.add_argument("--dry-run", action="store_true",
                        help="print what would be filed and exit")
    args = parser.parse_args(argv)

    order = [tid for wave in backlog.waves() for tid in wave]

    if args.dry_run:
        for tid in order:
            title, layer, blocked, *_ = backlog.TICKETS[tid]
            print(f"\n{'=' * 78}\n{tid}  [{layer}]  {title}\n{'=' * 78}")
            print(backlog.body(tid))
        return 0

    repo = args.repo
    seen = existing_issues(repo)
    numbers: dict[str, int] = {}

    # Pass 1 -- create the issues, parents first, so bodies can cite real numbers.
    for tid in order:
        title = backlog.TICKETS[tid][0]
        if title in seen:
            numbers[tid] = seen[title]
            print(f"{DIM}  exists {RESET}{tid}  #{seen[title]}  {title}")
            continue
        number = create_issue(repo, title, backlog.body(tid, numbers))
        numbers[tid] = number
        print(f"{GREEN}  created{RESET} {tid}  #{number}  {title}")

    # Pass 2 -- record the blocking edges as real dependencies.
    db_ids = {tid: issue_db_id(repo, n) for tid, n in numbers.items()}
    edges = failures = 0
    for tid in order:
        deps = backlog.TICKETS[tid][2]
        if not deps:
            continue
        current = blocked_by(repo, numbers[tid])
        for dep in deps:
            edges += 1
            if numbers[dep] in current:
                print(f"{DIM}  exists {RESET}#{numbers[tid]} blocked by #{numbers[dep]}"
                      f"  ({tid} <- {dep})")
                continue
            try:
                add_blocked_by(repo, numbers[tid], db_ids[dep])
                print(f"{GREEN}  linked {RESET}#{numbers[tid]} blocked by #{numbers[dep]}"
                      f"  ({tid} <- {dep})")
            except GhError as exc:
                failures += 1
                print(f"{RED}  failed {RESET}{tid} <- {dep}: "
                      f"{str(exc).splitlines()[0]}", file=sys.stderr)

    print(f"\n{len(numbers)} issues, {edges} blocking edges, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
