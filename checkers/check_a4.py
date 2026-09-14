"""Check the machine-verifiable half of Assignment A4 against a pair of Instances.

A4 is paired: the student opens the review-drill PR on their own Instance (with
`seed/tools/plant_review_pr.py`), the peer reviews it, the student answers review as the
author, and the student's own review of the *peer's* PR is written up on the student's
Instance. So the checker takes two handles and reads two things from the student's
Instance: the drill PR (as author, reviewed by the peer) and `a4-writeup.md` (as reviewer
of the peer's PR).

    python checkers/check_a4.py --org ORG --handle alice --peer bob
    python checkers/check_a4.py --org ORG --pairs pairs.txt      # "alice bob" per line, both directions
    python checkers/check_a4.py --org ORG --handle alice --peer bob --json

It grades *evidence*, never judgement: that a review with a verdict exists, that inline
comments and a suggestion block exist, that a thread was resolved, that the author pushed
after the verdict and re-requested review after pushing, that issues with `/qa`'s body
shape were filed and the PR's file set did not grow. Whether the comments were actionable,
whether the findings were classified correctly, and whether the out-of-scope call was
right are the rubric's job.

Requires an authenticated `gh` >= 2.94.0 on PATH. Exits non-zero if any run has a
failing check.

Every rule here was exercised against `perro-ruidoso/flashcards-w3probe` (PR #15) on
2026-09-14, the throwaway the Week 4 pages were built on, and fault-injected by replaying
a recorded snapshot of the `gh` responses with one mutation per rule.
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

DRILL_FILE = "src/flashcards/domain/scheduler.py"
DRILL_FILES = {DRILL_FILE, "tests/domain/test_scheduler.py"}
VERDICTS = {"APPROVED", "CHANGES_REQUESTED"}
SUGGESTION = "```suggestion"
# The installed /qa skill's issue templates (single issue, and one slice of a breakdown).
QA_HEADINGS = [
    re.compile(r"^## (What happened|What's wrong)", re.I | re.M),
    re.compile(r"^## What I expected", re.I | re.M),
    re.compile(r"^## Steps to reproduce", re.I | re.M),
]
MIN_INLINE_COMMENTS = 2

WRITEUP = "a4-writeup.md"
WRITEUP_MIN_WORDS = 300
WRITEUP_AXES = ["## Standards", "## Spec"]
WRITEUP_VERDICTS = ["must-fix", "nit", "false positive"]

# `gh pr list` with reviews, commits, and files for 100 PRs exceeds GitHub's GraphQL node
# limit ("requesting up to 1,000,000 possible nodes"), so the list carries only what is
# needed to pick the drill PR, and `gh pr view` fetches the rest for that one.
PR_LIST_FIELDS = "number,state,author,createdAt,headRefName,files"
PR_FIELDS = ",".join([
    "number", "title", "body", "state", "author", "createdAt", "mergedAt", "closedAt",
    "baseRefName", "headRefName", "changedFiles", "files", "closingIssuesReferences",
    "reviewDecision", "reviews", "reviewRequests", "commits",
])
ISSUE_FIELDS = "number,title,body,state,labels,issueType,createdAt,author"

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


@dataclass
class Result:
    handle: str
    peer: str
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


def same_login(a: str | None, b: str | None) -> bool:
    return (a or "").lower() == (b or "").lower()


# ---------------------------------------------------------------------------
# reads


def review_comments(repo: str, number: int) -> list[dict]:
    """Inline (diff) comments on the PR - the review-comments endpoint, not issue comments."""
    return gh_json("api", f"repos/{repo}/pulls/{number}/comments", "--paginate") or []


def review_threads(repo: str, number: int) -> list[dict]:
    owner, name = repo.split("/")
    query = (
        '{ repository(owner:"%s", name:"%s") { pullRequest(number:%d) { '
        "reviewThreads(first:100) { nodes { id isResolved isOutdated path "
        "resolvedBy { login } comments(first:1) { nodes { author { login } createdAt } } } } } } }"
    ) % (owner, name, number)
    data = gh_json("api", "graphql", "-f", f"query={query}")
    return data["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]


def review_requests(repo: str, number: int) -> list[dict]:
    """Every review_requested event: who asked, who was asked, when."""
    owner, name = repo.split("/")
    query = (
        '{ repository(owner:"%s", name:"%s") { pullRequest(number:%d) { '
        "timelineItems(itemTypes:[REVIEW_REQUESTED_EVENT], first:100) { nodes { "
        "... on ReviewRequestedEvent { createdAt actor { login } "
        "requestedReviewer { ... on User { login } } } } } } } }"
    ) % (owner, name, number)
    data = gh_json("api", "graphql", "-f", f"query={query}")
    out = []
    for node in data["data"]["repository"]["pullRequest"]["timelineItems"]["nodes"]:
        out.append({"at": node["createdAt"], "by": (node.get("actor") or {}).get("login"),
                    "reviewer": (node.get("requestedReviewer") or {}).get("login")})
    return out


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


def find_drill_pr(repo: str, prs: list[dict], peer: str) -> dict | None:
    """The review-drill PR: touches the scheduler module. If several do, prefer the one
    the peer reviewed, then the most recent. Returns the full `gh pr view` record."""
    drills = [pr for pr in prs if DRILL_FILE in {f["path"] for f in pr.get("files") or []}]
    if not drills:
        return None
    full = [gh_json("pr", "view", str(pr["number"]), "--repo", repo, "--json", PR_FIELDS)
            for pr in sorted(drills, key=lambda pr: pr["createdAt"], reverse=True)[:5]]
    reviewed = [pr for pr in full
                if any(same_login(r["author"]["login"], peer) for r in pr.get("reviews") or [])]
    pool = reviewed or full
    return max(pool, key=lambda pr: pr["createdAt"])


def peer_reviews(pr: dict, peer: str) -> list[dict]:
    return sorted((r for r in pr.get("reviews") or [] if same_login(r["author"]["login"], peer)),
                  key=lambda r: r["submittedAt"])


def check_verdict(res: Result, pr: dict, peer: str) -> dict | None:
    """M19: the peer submitted a review with a verdict, not just comments."""
    verdicts = [r for r in peer_reviews(pr, peer) if r["state"] in VERDICTS]
    if not verdicts:
        states = sorted({r["state"] for r in peer_reviews(pr, peer)}) or ["none"]
        res.add("Peer's review carries a verdict (M19)", False,
                f"{peer}'s reviews on #{pr['number']}: {', '.join(states)} - need APPROVED or CHANGES_REQUESTED")
        return None
    first = verdicts[0]
    res.add("Peer's review carries a verdict (M19)", True,
            f"#{pr['number']}: {first['state']} by {peer} at {first['submittedAt']}"
            + (f"; latest {verdicts[-1]['state']} at {verdicts[-1]['submittedAt']}" if len(verdicts) > 1 else ""))
    return first


def check_inline(res: Result, repo: str, pr: dict, peer: str) -> list[dict]:
    """M19: inline comments on the diff, batched or not, and at least one suggestion."""
    comments = [c for c in review_comments(repo, pr["number"]) if same_login(c["user"]["login"], peer)]
    top = [c for c in comments if not c.get("in_reply_to_id")]
    res.add("Peer left inline comments on the diff (M19)", len(top) >= MIN_INLINE_COMMENTS,
            f"{len(top)} by {peer} on {sorted({c['path'] for c in top})}" if top
            else f"no review comments by {peer} on #{pr['number']} (need {MIN_INLINE_COMMENTS}+)")
    suggestions = [c for c in comments if SUGGESTION in (c.get("body") or "")]
    res.add("Peer proposed a suggested change (M19)", bool(suggestions),
            f"{len(suggestions)} suggestion block(s), first on {suggestions[0]['path']}" if suggestions
            else "no ```suggestion block in the peer's comments")
    return comments


def check_threads(res: Result, repo: str, pr: dict) -> None:
    """M20: at least one conversation resolved."""
    threads = review_threads(repo, pr["number"])
    resolved = [t for t in threads if t["isResolved"]]
    res.add("A review thread was resolved (M20)", bool(resolved),
            f"{len(resolved)} of {len(threads)} resolved"
            + (f"; first by {(resolved[0].get('resolvedBy') or {}).get('login')}" if resolved else "")
            if threads else "no review threads on the PR")


def check_followup(res: Result, pr: dict, handle: str, verdict: dict | None) -> str | None:
    """M23: the author pushed after the peer's verdict. Returns the last such commit's date."""
    if not verdict:
        res.add("Author pushed after the peer's verdict (M23)", False, "no verdict to follow up")
        return None
    after = [c for c in pr.get("commits") or [] if c["committedDate"] > verdict["submittedAt"]]
    if not after:
        res.add("Author pushed after the peer's verdict (M23)", False,
                f"no commit on #{pr['number']} after {verdict['submittedAt']}")
        return None
    last = max(after, key=lambda c: c["committedDate"])
    res.add("Author pushed after the peer's verdict (M23)", True,
            f"{len(after)} commit(s) after {verdict['submittedAt']}; last {last['oid'][:7]} at {last['committedDate']}")
    return last["committedDate"]


def check_rerequest(res: Result, repo: str, pr: dict, peer: str, pushed_at: str | None) -> None:
    """M20/M23: review re-requested from the peer after the follow-up commits."""
    requests = [r for r in review_requests(repo, pr["number"]) if same_login(r["reviewer"], peer)]
    if not pushed_at:
        res.add("Review re-requested after the new commits (M20/M23)", False, "no follow-up commit to re-request after")
        return
    late = [r for r in requests if r["at"] > pushed_at]
    res.add("Review re-requested after the new commits (M20/M23)", bool(late),
            f"review_requested {peer} at {late[0]['at']} (last commit {pushed_at})" if late
            else f"{len(requests)} request(s) for {peer}, none after the last commit at {pushed_at}")


def check_rereview(res: Result, pr: dict, peer: str, pushed_at: str | None) -> None:
    """Note for the grader: did the peer come back after the push?"""
    if not pushed_at:
        return
    later = [r for r in peer_reviews(pr, peer) if r["submittedAt"] > pushed_at and r["state"] in VERDICTS]
    res.add("Peer re-reviewed after the push", None,
            f"{later[-1]['state']} at {later[-1]['submittedAt']}" if later
            else f"no verdict from {peer} after {pushed_at}; reviewDecision is {pr.get('reviewDecision') or 'empty'}")


def qa_shaped(body: str | None) -> bool:
    return all(p.search(body or "") for p in QA_HEADINGS)


def check_qa_issues(res: Result, pr: dict, issues: list[dict]) -> list[dict]:
    """M24: issues with /qa's body shape, filed after the PR opened."""
    filed = [i for i in issues if i["createdAt"] > pr["createdAt"] and qa_shaped(i.get("body"))]
    res.add("Issues filed with /qa's body shape after the PR opened (M24)", bool(filed),
            ", ".join(f"#{i['number']}" for i in filed) if filed
            else "no issue created after the PR has 'What happened / What I expected / Steps to reproduce'")
    if filed:
        labels = sorted({lb["name"] for i in filed for lb in i.get("labels") or []})
        types = sorted({(i.get("issueType") or {}).get("name") or "none" for i in filed})
        res.add("Labels and type on the /qa issues", None,
                f"labels {labels or 'none'}, type {types} - the installed /qa applies none; triage is Week 6")
    return filed


def check_scope(res: Result, pr: dict, qa: list[dict]) -> None:
    """M24: the PR did not absorb the out-of-scope work."""
    files = {f["path"] for f in pr.get("files") or []}
    extra = sorted(files - DRILL_FILES)
    res.add("PR's file set is still the drill's two files (M24)", not extra,
            f"{len(files)} file(s)" if not extra else "also touches " + ", ".join(extra))
    closes = {ref["number"] for ref in pr.get("closingIssuesReferences") or []}
    absorbed = sorted(closes & {i["number"] for i in qa})
    res.add("PR does not close the /qa issues (M24)", not absorbed,
            "" if not absorbed else "PR body closes " + ", ".join(f"#{n}" for n in absorbed))


def check_writeup(res: Result, repo: str) -> None:
    """M21/M22: the student's write-up of their review of the peer's PR."""
    try:
        raw = gh("api", f"repos/{repo}/contents/{WRITEUP}", "--jq", ".content")
        text = base64.b64decode(raw.strip().replace("\n", "")).decode("utf-8", "replace")
    except GhError:
        res.add(f"{WRITEUP} present", False, "not found on the default branch")
        return
    res.add(f"{WRITEUP} present", True)
    words = len(text.split())
    res.add("Write-up length", words >= WRITEUP_MIN_WORDS, f"{words} words (need {WRITEUP_MIN_WORDS}+)")
    axes = [a for a in WRITEUP_AXES if a.lower() in text.lower()]
    res.add("Write-up pastes /code-review's Standards and Spec output (M21)", len(axes) == len(WRITEUP_AXES),
            "both headings present" if len(axes) == 2 else f"found {axes or 'neither heading'}")
    verdicts = [v for v in WRITEUP_VERDICTS if v in text.lower()]
    res.add("Write-up classifies findings as must-fix / nit / false positive (M21)",
            None if len(verdicts) == len(WRITEUP_VERDICTS) else False,
            f"uses {', '.join(verdicts)}" if verdicts else "none of the three verdict words appears")


def check_student(org: str, handle: str, peer: str) -> Result:
    res = Result(handle, peer)
    repo = f"{org}/flashcards-{handle}"
    if not check_repo(res, repo):
        return res
    try:
        prs = gh_json("pr", "list", "--repo", repo, "--state", "all", "--limit", "100", "--json", PR_LIST_FIELDS) or []
        issues = gh_json("issue", "list", "--repo", repo, "--state", "all", "--limit", "200", "--json", ISSUE_FIELDS) or []
    except GhError as exc:
        res.add("PRs and issues readable", False, str(exc).splitlines()[0])
        return res

    try:
        pr = find_drill_pr(repo, prs, peer)
    except GhError as exc:
        res.add("Review-drill PR found", False, str(exc).splitlines()[0])
        return res
    if not pr:
        res.add("Review-drill PR found", False, f"no PR on {repo} touches {DRILL_FILE}")
        check_writeup(res, repo)
        return res
    res.add("Review-drill PR found", True,
            f"#{pr['number']} {pr['state']}, head {pr['headRefName']}, opened {pr['createdAt']}")
    res.add("Drill PR authored by the student", same_login(pr["author"]["login"], handle),
            f"author {pr['author']['login']}" + ("" if same_login(pr["author"]["login"], handle)
                                                 else f" - expected {handle}; an author cannot approve or request changes on it"))

    verdict = check_verdict(res, pr, peer)
    check_inline(res, repo, pr, peer)
    check_threads(res, repo, pr)
    pushed_at = check_followup(res, pr, handle, verdict)
    check_rerequest(res, repo, pr, peer, pushed_at)
    check_rereview(res, pr, peer, pushed_at)
    qa = check_qa_issues(res, pr, issues)
    check_scope(res, pr, qa)
    check_writeup(res, repo)
    return res


def render(res: Result) -> None:
    status = f"{RED}FAIL{RESET}" if res.failed else f"{GREEN}PASS{RESET}"
    print(f"\n{res.handle}  (peer: {res.peer})  [{status}]")
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
    group.add_argument("--handle", help="the student whose Instance holds the drill PR")
    group.add_argument("--pairs", type=Path, help="file with 'student peer' per line; both directions are checked")
    parser.add_argument("--peer", help="the reviewing peer's GitHub handle (with --handle)")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit machine-readable results instead of a report")
    args = parser.parse_args(argv)
    if args.handle and not args.peer:
        parser.error("--handle needs --peer")

    if shutil.which("gh") is None:
        print("gh CLI not found on PATH", file=sys.stderr)
        return 2
    ver = gh_version()
    if ver < MIN_GH:
        print(f"gh {'.'.join(map(str, ver))} is too old: this checker needs "
              f"{'.'.join(map(str, MIN_GH))}+", file=sys.stderr)
        return 2

    if args.handle:
        runs = [(args.handle, args.peer)]
    else:
        runs = []
        for ln in args.pairs.read_text(encoding="utf-8").splitlines():
            parts = ln.split()
            if len(parts) != 2 or ln.startswith("#"):
                continue
            a, b = parts
            runs += [(a, b), (b, a)]

    results = [check_student(args.org, h, p) for h, p in runs]

    if args.as_json:
        print(json.dumps([{"handle": r.handle, "peer": r.peer, "passed": not r.failed,
                           "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in r.checks]}
                          for r in results], indent=2))
    else:
        for res in results:
            render(res)
        failed = [f"{r.handle}" for r in results if r.failed]
        print(f"\n{len(results) - len(failed)}/{len(results)} passing")
        if failed:
            print(f"{RED}needs work:{RESET} {', '.join(failed)}")

    return 1 if any(r.failed for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
