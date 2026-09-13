"""Check the machine-verifiable half of Assignment A2 against a student's Instance.

Grades repository *state* - labels, the template, the spec, the ticket graph, the
GitHub side of the Linear probe - not judgement. Slice quality, edge honesty, and the
Linear captures are a human's job.

    python checkers/check_a2.py --org ORG --handle alice
    python checkers/check_a2.py --org ORG --handles handles.txt
    python checkers/check_a2.py --org ORG --handle alice --json

Requires an authenticated `gh` >= 2.94.0 on PATH: the checks read `issueType`, `parent`,
`blockedBy`, and `subIssuesSummary`, which older releases do not expose. Exits non-zero
if any student has a failing check.
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
from pathlib import Path

MIN_GH = (2, 94, 0)

LAYER_LABELS = ["layer:domain", "layer:storage", "layer:cli"]
READY = "ready-for-agent"

TICKET_HEADINGS = ["## Context", "## Acceptance criteria", "## Out of scope", "## Blocked by"]
SPEC_HEADINGS = [
    "## Problem Statement", "## Solution", "## User Stories", "## Implementation Decisions",
    "## Testing Decisions", "## Out of Scope", "## Further Notes",
]

TICKETS_MIN, TICKETS_MAX = 6, 10
EDGES_MIN = 6

PROBE_PREFIX = "sync probe"
LINEAR_ID = re.compile(r"\b[A-Z][A-Z0-9]{1,9}-\d+\b")

WRITEUP = "a2-writeup.md"
WRITEUP_MIN_WORDS = 250

ISSUE_FIELDS = ",".join([
    "number", "title", "body", "state", "stateReason", "createdAt", "labels", "issueType",
    "parent", "blockedBy", "subIssuesSummary", "comments",
])

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


# ---------------------------------------------------------------------------
# helpers over the issue list


def label_names(issue: dict) -> set[str]:
    return {lbl["name"] for lbl in issue.get("labels") or []}


def type_name(issue: dict) -> str | None:
    t = issue.get("issueType")
    return t.get("name") if isinstance(t, dict) else None


def parent_number(issue: dict) -> int | None:
    p = issue.get("parent")
    return p.get("number") if isinstance(p, dict) else None


def blockers(issue: dict) -> set[int]:
    bb = issue.get("blockedBy") or {}
    return {n["number"] for n in bb.get("nodes") or []}


def has_headings(body: str, headings: list[str]) -> bool:
    return all(h.lower() in (body or "").lower() for h in headings)


def kahn(numbers: set[int], edges: dict[int, set[int]]) -> tuple[list[list[int]], list[int]]:
    """Waves, and the leftover nodes if a cycle stops the sort."""
    remaining = {n: {b for b in edges.get(n, set()) if b in numbers} for n in numbers}
    waves: list[list[int]] = []
    while remaining:
        ready = sorted(n for n, bs in remaining.items() if not bs)
        if not ready:
            return waves, sorted(remaining)
        waves.append(ready)
        for n in ready:
            del remaining[n]
        for bs in remaining.values():
            bs.difference_update(ready)
    return waves, []


# ---------------------------------------------------------------------------
# checks


def check_repo(res: Result, repo: str) -> bool:
    try:
        gh_json("repo", "view", repo, "--json", "name")
    except GhError as exc:
        res.add("Instance exists", False, f"{repo}: {str(exc).splitlines()[0]}")
        return False
    res.add("Instance exists", True, repo)
    return True


def check_labels(res: Result, repo: str) -> None:
    try:
        names = {l["name"] for l in gh_json("label", "list", "--repo", repo, "--json", "name", "--limit", "100") or []}
    except GhError as exc:
        res.add("Layer labels", False, str(exc).splitlines()[0])
        return
    missing = [l for l in LAYER_LABELS if l not in names]
    res.add("Layer labels (3)", not missing, "" if not missing else f"missing: {', '.join(missing)}")
    if READY not in names:
        res.add(f"Label {READY}", False, "missing - A1 created it; the skills apply it")


def check_template(res: Result, repo: str) -> None:
    try:
        entries = gh_json("api", f"repos/{repo}/contents/.github/ISSUE_TEMPLATE")
    except GhError:
        res.add("Issue template", False, ".github/ISSUE_TEMPLATE/ not on the default branch")
        return
    md = [e for e in entries or [] if e.get("name", "").endswith(".md")]
    if not md:
        res.add("Issue template", False, "no .md template in .github/ISSUE_TEMPLATE/")
        return
    name = md[0]["name"]
    try:
        raw = gh("api", f"repos/{repo}/contents/.github/ISSUE_TEMPLATE/{name}", "--jq", ".content")
        text = base64.b64decode(raw.strip().replace("\n", "")).decode("utf-8", "replace")
    except GhError:
        res.add("Issue template", False, f"could not read {name}")
        return
    res.add("Issue template", True, name)
    front = text.split("---")[1] if text.startswith("---") and text.count("---") >= 2 else ""
    res.add("Template front matter sets type", bool(re.search(r"^\s*type:\s*\S", front, re.M)),
            "" if "type:" in front else "no `type:` key")
    res.add("Template has the four headings", has_headings(text, TICKET_HEADINGS),
            "" if has_headings(text, TICKET_HEADINGS) else "a heading is missing")
    # A pre-filled criterion is one that names a real path or a concrete assertion. Cheap
    # proxy: any checklist line mentioning tests/ or src/ is content, not a prompt.
    prefilled = re.search(r"^- \[ \].*(tests/|src/)", text, re.M)
    res.add("Template criteria are prompts, not content", None if not prefilled else False,
            "for the human grader" if not prefilled else f"pre-filled: {prefilled.group(0).strip()[:60]}")


def check_metadata(res: Result, open_issues: list[dict]) -> None:
    unlabelled = [i["number"] for i in open_issues if not label_names(i)]
    untyped = [i["number"] for i in open_issues if not type_name(i)]
    res.add("Every open issue has a label", not unlabelled,
            "" if not unlabelled else "no:label -> " + ", ".join(f"#{n}" for n in unlabelled))
    res.add("Every open issue has a type", not untyped,
            "" if not untyped else "untyped: " + ", ".join(f"#{n}" for n in untyped))


def find_spec(open_issues: list[dict]) -> dict | None:
    specs = [i for i in open_issues if has_headings(i.get("body"), SPEC_HEADINGS)]
    # Prefer one that is a parent; then the oldest.
    specs.sort(key=lambda i: (-(i.get("subIssuesSummary") or {}).get("total", 0), i["createdAt"]))
    return specs[0] if specs else None


def check_hand_ticket(res: Result, open_issues: list[dict], spec: dict | None) -> None:
    spec_n = spec["number"] if spec else None
    cands = [i for i in open_issues
             if has_headings(i.get("body"), TICKET_HEADINGS)
             and parent_number(i) != spec_n
             and "layer:domain" in label_names(i)]
    if not cands:
        res.add("Hand-written ticket (M07)", False,
                "no open issue with the four headings, layer:domain, outside the spec's children")
        return
    t = sorted(cands, key=lambda i: i["createdAt"])[0]
    res.add("Hand-written ticket (M07)", True, f"#{t['number']} {t['title'][:50]} - rubric grades it")
    names_test = bool(re.search(r"tests?/\S+\.py", t.get("body") or ""))
    res.add("Hand ticket names a test file", None if names_test else False,
            "for the human grader" if names_test else "no tests/...py path in the criteria")


def check_spec(res: Result, spec: dict | None) -> None:
    if spec is None:
        res.add("Spec issue (M09)", False, "no open issue with the seven spec headings")
        return
    n = spec["number"]
    res.add("Spec issue (M09)", True, f"#{n} {spec['title'][:50]}")
    res.add("Spec labelled ready-for-agent", READY in label_names(spec))
    res.add("Spec typed Feature", type_name(spec) == "Feature", f"type={type_name(spec)}")
    fence = "```mermaid" in (spec.get("body") or "")
    res.add("Spec body has a mermaid fence (M11)", fence, "" if fence else "paste waves_from_github.py --mermaid output")


def check_tickets(res: Result, open_issues: list[dict], spec: dict | None) -> None:
    if spec is None:
        res.add("Tickets (M10)", False, "no spec to hang tickets on")
        return
    tickets = [i for i in open_issues if parent_number(i) == spec["number"]]
    count = len(tickets)
    res.add("Tickets are sub-issues of the spec", TICKETS_MIN <= count <= TICKETS_MAX,
            f"{count} open tickets with parent #{spec['number']} (need {TICKETS_MIN}-{TICKETS_MAX})")
    if not tickets:
        return

    not_task = [t["number"] for t in tickets if type_name(t) != "Task"]
    not_ready = [t["number"] for t in tickets if READY not in label_names(t)]
    no_layer = [t["number"] for t in tickets if not (label_names(t) & set(LAYER_LABELS))]
    res.add("Every ticket typed Task", not not_task,
            "" if not not_task else ", ".join(f"#{n}" for n in not_task))
    res.add("Every ticket labelled ready-for-agent", not not_ready,
            "" if not not_ready else ", ".join(f"#{n}" for n in not_ready))
    res.add("Every ticket has a layer label", not no_layer,
            "" if not no_layer else ", ".join(f"#{n}" for n in no_layer))

    numbers = {t["number"] for t in tickets}
    edges = {t["number"]: blockers(t) & numbers for t in tickets}
    edge_count = sum(len(v) for v in edges.values())
    joins = sorted(n for n, bs in edges.items() if len(bs) >= 2)
    res.add("Blocking edges recorded (M11)", edge_count >= EDGES_MIN,
            f"{edge_count} edges among the tickets (need {EDGES_MIN}+)")
    res.add("At least one two-parent join", bool(joins),
            "joins: " + ", ".join(f"#{n}" for n in joins) if joins else "no ticket has two blockers")

    waves, stuck = kahn(numbers, edges)
    if stuck:
        res.add("Graph is a DAG", False, "cycle among " + ", ".join(f"#{n}" for n in stuck))
    else:
        width = max(len(w) for w in waves)
        res.add("Graph is a DAG", True, f"{len(waves)} waves, max parallel width {width}")

    # Blocked-by prose without a recorded edge: a warning, since the skill may have
    # written the number in the body and not the relation.
    prose_only = []
    for t in tickets:
        body = t.get("body") or ""
        m = re.search(r"## Blocked by(.*?)(?:\n## |\Z)", body, re.S | re.I)
        if not m:
            continue
        cited = {int(x) for x in re.findall(r"#(\d+)", m.group(1))} & numbers
        if cited - blockers(t):
            prose_only.append(f"#{t['number']} cites {sorted(cited - blockers(t))} in prose only")
    res.add("Body Blocked-by lines are recorded edges", None if not prose_only else False,
            "; ".join(prose_only) if prose_only else "")


def check_probe(res: Result, all_issues: list[dict], spec: dict | None, repo: str) -> None:
    probes = [i for i in all_issues if (i.get("title") or "").lower().startswith(PROBE_PREFIX)]
    if not probes:
        res.add("Sync probe issue (M12)", False, f"no issue titled '{PROBE_PREFIX.title()}...'")
        return
    p = sorted(probes, key=lambda i: i["createdAt"])[-1]
    res.add("Sync probe issue (M12)", True, f"#{p['number']}")
    if spec:
        res.add("Probe created after the spec", p["createdAt"] > spec["createdAt"],
                f"probe {p['createdAt']} vs spec {spec['createdAt']}")
    closed_ok = p.get("state") == "CLOSED" and p.get("stateReason") == "COMPLETED"
    res.add("Probe closed with reason completed", closed_ok,
            f"state={p.get('state')} reason={p.get('stateReason')}")
    n_comments = len(p.get("comments") or [])
    res.add("Probe has a comment from gh", n_comments >= 1, f"{n_comments} comment(s)")

    # The PR preview: a closed, unmerged PR whose title carries a Linear-style ID.
    try:
        prs = gh_json("pr", "list", "--repo", repo, "--state", "closed", "--limit", "50",
                      "--json", "number,title,mergedAt,headRefName") or []
    except GhError:
        prs = []
    hits = [pr for pr in prs if not pr.get("mergedAt") and LINEAR_ID.search(pr.get("title") or "")]
    res.add("PR preview with a Linear ID in the title", None,
            f"#{hits[0]['number']} {hits[0]['title'][:40]}" if hits else "none found - fine if Linear could not be wired; say so in the write-up")


def check_writeup(res: Result, repo: str) -> None:
    try:
        raw = gh("api", f"repos/{repo}/contents/{WRITEUP}", "--jq", ".content")
        text = base64.b64decode(raw.strip().replace("\n", "")).decode("utf-8", "replace")
    except GhError:
        res.add(f"{WRITEUP} present", False, "not found")
        return
    res.add(f"{WRITEUP} present", True)
    words = len(text.split())
    res.add("Write-up length", words >= WRITEUP_MIN_WORDS, f"{words} words (need {WRITEUP_MIN_WORDS}+)")
    has_capture = bool(re.search(r"!\[|\.(png|jpe?g|gif|webp)\b", text, re.I))
    res.add("Write-up references a capture", None if has_capture else False,
            "for the human grader" if has_capture else "no image reference for the Linear evidence")


def check_student(org: str, handle: str) -> Result:
    res = Result(handle)
    repo = f"{org}/flashcards-{handle}"
    if not check_repo(res, repo):
        return res
    check_labels(res, repo)
    check_template(res, repo)
    try:
        all_issues = gh_json("issue", "list", "--repo", repo, "--state", "all", "--limit", "200",
                             "--json", ISSUE_FIELDS) or []
    except GhError as exc:
        res.add("Issues readable", False, str(exc).splitlines()[0])
        return res
    open_issues = [i for i in all_issues if i.get("state") == "OPEN"]
    spec = find_spec(open_issues)
    check_metadata(res, open_issues)
    check_hand_ticket(res, open_issues, spec)
    check_spec(res, spec)
    check_tickets(res, open_issues, spec)
    check_probe(res, all_issues, spec, repo)
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
              f"{'.'.join(map(str, MIN_GH))}+ for --json issueType,parent,blockedBy", file=sys.stderr)
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
