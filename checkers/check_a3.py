"""Check the machine-verifiable half of Assignment A3 against a student's Instance.

Grades repository *state* - branch names, PR bodies, closing links, the retarget event,
the merge commit that resolved a conflict, the auto-closed issues - not judgement. Whether
a diff was reviewable, whether the PR body's risk section is honest, and whether the
conflict was explained correctly are a human's job.

    python checkers/check_a3.py --org ORG --handle alice
    python checkers/check_a3.py --org ORG --handles handles.txt
    python checkers/check_a3.py --org ORG --handle alice --json

Requires an authenticated `gh` >= 2.94.0 on PATH: the checks read `blockedBy`, which
older releases do not expose. Exits non-zero if any student has a failing check.

Every rule here was exercised against `perro-ruidoso/flashcards-w3probe` on 2026-09-13,
the throwaway Instance the Week 3 pages were built on.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

MIN_GH = (2, 94, 0)

PR_HEADINGS = ["## Intent", "## Scope", "## Verification", "## Risk"]
CLOSING_KEYWORD = re.compile(
    r"\b(close[sd]?|fix(e[sd])?|resolve[sd]?)\b:?\s*#(\d+)", re.I
)
# A `gh issue develop` branch, with or without --name, starts with the issue number.
BRANCH_FROM_ISSUE = re.compile(r"^(\d+)-")

# A linked issue closes within this many seconds of the merge when a keyword did it.
AUTO_CLOSE_WINDOW_S = 30

WRITEUP = "a3-writeup.md"
WRITEUP_MIN_WORDS = 200

PR_FIELDS = ",".join([
    "number", "title", "body", "state", "mergedAt", "closedAt", "createdAt",
    "baseRefName", "headRefName", "changedFiles", "closingIssuesReferences",
])
ISSUE_FIELDS = "number,title,state,stateReason,closedAt,createdAt,blockedBy"

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


@dataclass
class Result:
    handle: str
    checks: list[tuple[str, bool | None, str]] = field(default_factory=list)

    def add(self, name: str, ok: bool | None, detail: str = "") -> None:
        self.checks.append((name, ok, detail))

    @property
    def failed(self) -> bool:
        return any(ok is False for _, ok, _ in self.checks)


class GhError(RuntimeError):
    pass


def gh(*args: str) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise GhError((proc.stderr or proc.stdout).strip())
    return proc.stdout


def gh_json(*args: str):
    return json.loads(gh(*args) or "null")


def gh_version() -> tuple[int, ...]:
    first = gh("--version").splitlines()[0]
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", first)
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


def ts(s: str | None) -> datetime | None:
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def seconds_between(a: str | None, b: str | None) -> float | None:
    da, db = ts(a), ts(b)
    return (db - da).total_seconds() if da and db else None


# ---------------------------------------------------------------------------
# helpers over PRs and issues


def closes(pr: dict) -> set[int]:
    return {ref["number"] for ref in pr.get("closingIssuesReferences") or []}


def blockers(issue: dict) -> set[int]:
    bb = issue.get("blockedBy") or {}
    return {n["number"] for n in bb.get("nodes") or []}


def has_headings(body: str | None, headings: list[str]) -> list[str]:
    text = (body or "").lower()
    return [h for h in headings if h.lower() not in text]


def base_changes(repo: str, number: int) -> list[dict]:
    """Every base-branch change on a PR: manual (BaseRefChangedEvent) or GitHub's own
    retarget after the parent branch was deleted (AutomaticBaseChangeSucceededEvent)."""
    owner, name = repo.split("/")
    query = (
        '{ repository(owner:"%s", name:"%s") { pullRequest(number:%d) { '
        "timelineItems(itemTypes:[BASE_REF_CHANGED_EVENT, AUTOMATIC_BASE_CHANGE_SUCCEEDED_EVENT], first:20) "
        "{ nodes { __typename "
        "... on BaseRefChangedEvent { createdAt previousRefName currentRefName } "
        "... on AutomaticBaseChangeSucceededEvent { createdAt oldBase newBase } } } } } }"
    ) % (owner, name, number)
    data = gh_json("api", "graphql", "-f", f"query={query}")
    out = []
    for node in data["data"]["repository"]["pullRequest"]["timelineItems"]["nodes"]:
        if node["__typename"] == "BaseRefChangedEvent":
            out.append({"at": node["createdAt"], "from": node["previousRefName"],
                        "to": node["currentRefName"], "how": "gh pr edit --base"})
        else:
            out.append({"at": node["createdAt"], "from": node["oldBase"],
                        "to": node["newBase"], "how": "automatic"})
    return out


def merge_commits_in(repo: str, number: int) -> list[str]:
    """Two-parent commits on the PR branch: the trace `git merge main` leaves behind."""
    commits = gh_json("api", f"repos/{repo}/pulls/{number}/commits", "--paginate") or []
    return [c["sha"][:7] for c in commits if len(c.get("parents") or []) >= 2]


# ---------------------------------------------------------------------------
# checks


def check_repo(res: Result, repo: str) -> dict | None:
    try:
        info = gh_json("repo", "view", repo, "--json", "name,defaultBranchRef")
    except GhError as exc:
        res.add("Instance exists", False, f"{repo}: {str(exc).splitlines()[0]}")
        return None
    res.add("Instance exists", True, repo)
    return info


def merged_ticket_prs(prs: list[dict], issues: dict[int, dict]) -> list[dict]:
    """Merged PRs that link at least one issue of this repository."""
    return sorted(
        (pr for pr in prs if pr.get("mergedAt") and closes(pr) & set(issues)),
        key=lambda pr: pr["mergedAt"],
    )


def check_branches(res: Result, ticket_prs: list[dict]) -> None:
    """M13: every ticket PR's head branch is named from its issue."""
    bad = []
    for pr in ticket_prs:
        m = BRANCH_FROM_ISSUE.match(pr["headRefName"])
        if not m or int(m.group(1)) not in closes(pr):
            bad.append(f"#{pr['number']} head {pr['headRefName']!r} closes {sorted(closes(pr))}")
    res.add("Branch named from its issue (M13)", not bad,
            f"{len(ticket_prs)} merged ticket PR(s)" if not bad else "; ".join(bad))


def check_pr_bodies(res: Result, ticket_prs: list[dict]) -> None:
    """M15: the four sections and a closing keyword, in the body itself."""
    missing = []
    no_keyword = []
    for pr in ticket_prs:
        gaps = has_headings(pr.get("body"), PR_HEADINGS)
        if gaps:
            missing.append(f"#{pr['number']} lacks {', '.join(gaps)}")
        if not CLOSING_KEYWORD.search(pr.get("body") or ""):
            no_keyword.append(f"#{pr['number']}")
    res.add("PR body has Intent / Scope / Verification / Risk (M15)", not missing,
            "" if not missing else "; ".join(missing))
    res.add("PR body carries a closing keyword (M15)", not no_keyword,
            "" if not no_keyword else "no `Closes #n` in " + ", ".join(no_keyword))


def check_auto_close(res: Result, ticket_prs: list[dict], issues: dict[int, dict]) -> None:
    """M15/M06: the linked issue closed itself within seconds of the merge, as COMPLETED."""
    slow, wrong = [], []
    for pr in ticket_prs:
        for n in sorted(closes(pr)):
            issue = issues.get(n)
            if not issue:
                continue
            if issue.get("state") != "CLOSED" or issue.get("stateReason") != "COMPLETED":
                wrong.append(f"#{n} state={issue.get('state')} reason={issue.get('stateReason')}")
                continue
            gap = seconds_between(pr["mergedAt"], issue.get("closedAt"))
            if gap is None or gap < 0 or gap > AUTO_CLOSE_WINDOW_S:
                slow.append(f"#{n} closed {gap:+.0f}s from PR #{pr['number']}'s merge" if gap is not None
                            else f"#{n} has no closedAt")
    res.add("Linked issues closed as completed", not wrong, "" if not wrong else "; ".join(wrong))
    res.add("Issues auto-closed on merge (within %ds)" % AUTO_CLOSE_WINDOW_S, not slow,
            "" if not slow else "; ".join(slow))


def find_stack(repo: str, ticket_prs: list[dict], issues: dict[int, dict], default: str) -> tuple[dict | None, list[dict]]:
    """The first merged ticket PR whose base was changed onto the default branch."""
    for pr in ticket_prs:
        events = [e for e in base_changes(repo, pr["number"]) if e["to"] == default and e["from"] != default]
        if events:
            return pr, events
    return None, []


def check_stack(res: Result, repo: str, ticket_prs: list[dict], issues: dict[int, dict],
                prs_by_head: dict[str, dict], default: str) -> dict | None:
    """M16: a merged PR that started on another branch and was retargeted to main; the
    parent branch belongs to a merged PR whose issue blocks this one."""
    stacked, events = find_stack(repo, ticket_prs, issues, default)
    if not stacked:
        res.add("Stacked PR retargeted to the default branch (M16)", False,
                "no merged ticket PR has a base change onto " + default)
        return None
    ev = events[0]
    res.add("Stacked PR retargeted to the default branch (M16)", True,
            f"#{stacked['number']} base {ev['from']} -> {ev['to']} at {ev['at']} ({ev['how']})")

    parent = prs_by_head.get(ev["from"])
    if not parent or not parent.get("mergedAt"):
        res.add("Stack parent is a merged PR", False, f"no merged PR has head {ev['from']!r}")
        return stacked
    res.add("Stack parent is a merged PR", True, f"#{parent['number']} merged {parent['mergedAt']}")
    res.add("Retarget happened after the parent merged",
            (seconds_between(parent["mergedAt"], ev["at"]) or -1) >= 0,
            f"parent merged {parent['mergedAt']}, retarget {ev['at']}")

    child_issues = closes(stacked)
    parent_issues = closes(parent)
    honest = any(parent_issues & blockers(issues[n]) for n in child_issues if n in issues)
    res.add("Stacked PR's issue is blocked by the parent's issue", honest,
            f"child closes {sorted(child_issues)}, parent closes {sorted(parent_issues)}, "
            + ", ".join(f"#{n} blocked by {sorted(blockers(issues[n]))}" for n in sorted(child_issues) if n in issues))
    return stacked


def check_conflict(res: Result, repo: str, stacked: dict | None) -> None:
    """M17: the stacked branch carries a two-parent commit - the merge of main that the
    conflict was resolved in."""
    if not stacked:
        res.add("Conflict resolved on the stacked branch (M17)", False, "no stacked PR found")
        return
    merges = merge_commits_in(repo, stacked["number"])
    res.add("Conflict resolved on the stacked branch (M17)", bool(merges),
            f"merge commit(s) on #{stacked['number']}: {', '.join(merges)}" if merges
            else f"#{stacked['number']} has no two-parent commit; a rebase leaves no trace - explain in the write-up")


def check_split(res: Result, prs: list[dict], ticket_prs: list[dict]) -> None:
    """M14: one issue, two PRs - an earlier one closed unmerged, a later one merged with
    fewer files. The evidence of a split; the rubric grades the judgement."""
    by_issue: dict[int, list[dict]] = {}
    for pr in prs:
        for n in closes(pr):
            by_issue.setdefault(n, []).append(pr)
    found = []
    for n, group in by_issue.items():
        merged = [p for p in group if p.get("mergedAt")]
        abandoned = [p for p in group if p.get("closedAt") and not p.get("mergedAt")]
        for a in abandoned:
            for m in merged:
                if a["closedAt"] <= m["mergedAt"] and (a.get("changedFiles") or 0) > (m.get("changedFiles") or 0):
                    found.append(f"#{n}: #{a['number']} closed unmerged ({a['changedFiles']} files) -> #{m['number']} merged ({m['changedFiles']} files)")
    res.add("A drive-by PR was closed and re-opened smaller (M14)", bool(found),
            "; ".join(found) if found else "no issue has a closed-unmerged PR followed by a smaller merged one")


def check_writeup(res: Result, repo: str) -> None:
    try:
        raw = gh("api", f"repos/{repo}/contents/{WRITEUP}", "--jq", ".content")
        text = base64.b64decode(raw.strip().replace("\n", "")).decode("utf-8", "replace")
    except GhError:
        res.add(f"{WRITEUP} present", False, "not found on the default branch")
        return
    res.add(f"{WRITEUP} present", True)
    words = len(text.split())
    res.add("Write-up length", words >= WRITEUP_MIN_WORDS, f"{words} words (need {WRITEUP_MIN_WORDS}+)")
    names_conflict = bool(re.search(r"conflict", text, re.I))
    res.add("Write-up explains the conflict (M17)", None if names_conflict else False,
            "for the human grader" if names_conflict else "the word 'conflict' does not appear")
    names_skills = [s for s in ("wayfinder", "request-refactor-plan", "grill-me", "tdd", "handoff", "git-guardrails")
                    if s in text]
    res.add("Write-up names skills for the three situations (M18)", None if len(names_skills) >= 3 else False,
            f"mentions {', '.join(names_skills)}" if names_skills else "no skill named")


def check_student(org: str, handle: str) -> Result:
    res = Result(handle)
    repo = f"{org}/flashcards-{handle}"
    info = check_repo(res, repo)
    if not info:
        return res
    default = (info.get("defaultBranchRef") or {}).get("name") or "main"
    try:
        prs = gh_json("pr", "list", "--repo", repo, "--state", "all", "--limit", "100", "--json", PR_FIELDS) or []
        issue_list = gh_json("issue", "list", "--repo", repo, "--state", "all", "--limit", "200", "--json", ISSUE_FIELDS) or []
    except GhError as exc:
        res.add("PRs and issues readable", False, str(exc).splitlines()[0])
        return res
    issues = {i["number"]: i for i in issue_list}
    prs_by_head = {pr["headRefName"]: pr for pr in prs if pr.get("mergedAt")}

    ticket_prs = merged_ticket_prs(prs, issues)
    res.add("Merged PRs that link an issue", len(ticket_prs) >= 2,
            f"{len(ticket_prs)} (need 2+): " + ", ".join(f"#{p['number']}" for p in ticket_prs))
    if not ticket_prs:
        return res

    edge = any(blockers(issues[n]) & set(issues) for pr in ticket_prs for n in closes(pr) if n in issues)
    res.add("A blocking edge between the tickets (M11 recap)", edge,
            "" if edge else "no linked issue is blocked by another issue")

    check_branches(res, ticket_prs)
    check_pr_bodies(res, ticket_prs)
    check_auto_close(res, ticket_prs, issues)
    stacked = check_stack(res, repo, ticket_prs, issues, prs_by_head, default)
    check_conflict(res, repo, stacked)
    check_split(res, prs, ticket_prs)
    check_writeup(res, repo)
    return res


def render(res: Result) -> None:
    status = f"{RED}FAIL{RESET}" if res.failed else f"{GREEN}PASS{RESET}"
    print(f"\n{res.handle}  [{status}]")
    for name, ok, detail in res.checks:
        mark = f"{GREEN}ok  {RESET}" if ok is True else f"{RED}fail{RESET}" if ok is False else f"{YELLOW}note{RESET}"
        line = f"  {mark} {name}"
        if detail:
            line += f"  {DIM}{detail}{RESET}"
        print(line)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--org", required=True, help="course GitHub organization")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--handle", help="one student's GitHub handle")
    group.add_argument("--handles", type=Path, help="file with one GitHub handle per line")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit machine-readable results instead of a report")
    args = parser.parse_args(argv)

    if shutil.which("gh") is None:
        print("gh CLI not found on PATH", file=sys.stderr)
        return 2
    ver = gh_version()
    if ver < MIN_GH:
        print(f"gh {'.'.join(map(str, ver))} is too old: this checker needs "
              f"{'.'.join(map(str, MIN_GH))}+ for --json blockedBy", file=sys.stderr)
        return 2

    if args.handle:
        handles = [args.handle]
    else:
        handles = [ln.strip() for ln in args.handles.read_text(encoding="utf-8").splitlines()
                   if ln.strip() and not ln.startswith("#")]

    results = [check_student(args.org, h) for h in handles]

    if args.as_json:
        print(json.dumps([{"handle": r.handle, "passed": not r.failed,
                           "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in r.checks]}
                          for r in results], indent=2))
    else:
        for res in results:
            render(res)
        failed = [r.handle for r in results if r.failed]
        print(f"\n{len(results) - len(failed)}/{len(results)} passing")
        if failed:
            print(f"{RED}needs work:{RESET} {', '.join(failed)}")

    return 1 if any(r.failed for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
