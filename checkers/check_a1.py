"""Check the machine-verifiable half of Assignment A1 against a student's Instance.

Grades repository *state*, not prose — the written analysis is a human's job.

    python checkers/check_a1.py --org ORG --handle alice
    python checkers/check_a1.py --org ORG --handles handles.txt
    python checkers/check_a1.py --org ORG --handle alice --json

Requires an authenticated `gh` on PATH. Exits non-zero if any student has a failing
check, so it can be wired into CI later.
"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

TEMPLATE = "flashcards-seed"

REQUIRED_FILES = [
    "docs/agents/issue-tracker.md",
    "docs/agents/triage-labels.md",
    "docs/agents/domain.md",
]

# The four labels a student actually creates. The fifth, `wontfix`, is in GitHub's
# default label set and arrives on every new repository (verified 2026-09-12 by deleting
# it from the template and watching it reappear on a fresh Instance). It is checked for
# presence but reported as a note, not a pass -- decided 2026-09-13, see NOTES.md.
CREATED_LABELS = [
    "needs-triage",
    "needs-info",
    "ready-for-agent",
    "ready-for-human",
]
DEFAULT_LABELS = ["wontfix"]

# Labels take a few seconds to appear on a newly created repository: an immediate
# `gh label list` can return an empty set. Retry before calling anything missing.
LABEL_RETRIES = 3
LABEL_RETRY_SECONDS = 3.0

WRITEUP = "a1-writeup.md"
WRITEUP_MIN_WORDS = 250

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
    """Run a gh command, returning stdout. Raises GhError on failure."""
    proc = subprocess.run(
        ["gh", *args], capture_output=True, text=True, encoding="utf-8"
    )
    if proc.returncode != 0:
        raise GhError((proc.stderr or proc.stdout).strip())
    return proc.stdout


def gh_json(*args: str):
    return json.loads(gh(*args) or "null")


def _name_with_owner(tmpl: object) -> str | None:
    """Build OWNER/NAME from gh's templateRepository object, which omits it."""
    if not isinstance(tmpl, dict):
        return None
    name = tmpl.get("name")
    owner = tmpl.get("owner")
    login = owner.get("login") if isinstance(owner, dict) else None
    if not name or not login:
        return None
    return f"{login}/{name}"


def check_repo(res: Result, org: str, handle: str) -> dict | None:
    """Repository exists, is public, and was made from the template."""
    repo = f"{org}/flashcards-{handle}"
    try:
        data = gh_json(
            "repo", "view", repo,
            "--json", "name,visibility,isFork,templateRepository,defaultBranchRef",
        )
    except GhError as exc:
        res.add("Instance exists", False, f"{repo}: {str(exc).splitlines()[0]}")
        return None

    res.add("Instance exists", True, repo)
    res.add(
        "Public",
        data.get("visibility") == "PUBLIC",
        f"visibility={data.get('visibility')}",
    )

    # `gh repo view --json templateRepository` returns {id, name, owner{id, login}}
    # and *no* nameWithOwner -- verified against a real template instance on
    # 2026-09-12. Reading nameWithOwner here silently failed every student.
    tmpl = data.get("templateRepository") or {}
    tmpl_name = _name_with_owner(tmpl)
    expected = f"{org}/{TEMPLATE}"
    if data.get("isFork"):
        res.add("Created from template", False, "this is a fork, not a template instance")
    else:
        res.add(
            "Created from template",
            tmpl_name == expected,
            f"templateRepository={tmpl_name or 'null'} (expected {expected})",
        )
    return data


def check_files(res: Result, org: str, handle: str) -> None:
    """The three skill-config files are committed, and CLAUDE.md names them."""
    repo = f"{org}/flashcards-{handle}"
    for path in REQUIRED_FILES:
        try:
            gh("api", f"repos/{repo}/contents/{path}", "--silent")
            res.add(f"File {path}", True)
        except GhError:
            res.add(f"File {path}", False, "not found on the default branch")

    try:
        body = gh(
            "api", f"repos/{repo}/contents/CLAUDE.md",
            "--jq", ".content",
        )
        text = base64.b64decode(body.strip().replace("\n", "")).decode("utf-8", "replace")
        res.add(
            "CLAUDE.md has '## Agent skills'",
            "## Agent skills" in text,
            "" if "## Agent skills" in text else "section missing",
        )
    except GhError:
        res.add("CLAUDE.md has '## Agent skills'", False, "CLAUDE.md not found")


def _label_names(repo: str) -> set[str]:
    return {
        lbl["name"]
        for lbl in gh_json("label", "list", "--repo", repo, "--json", "name") or []
    }


def check_labels(res: Result, org: str, handle: str) -> None:
    repo = f"{org}/flashcards-{handle}"
    try:
        names = _label_names(repo)
        for _ in range(LABEL_RETRIES):
            if not names:
                time.sleep(LABEL_RETRY_SECONDS)
                names = _label_names(repo)
    except GhError as exc:
        res.add("Triage labels", False, str(exc).splitlines()[0])
        return

    missing = [lbl for lbl in CREATED_LABELS if lbl not in names]
    res.add(
        "Triage labels (4 created + 1 default)",
        not missing,
        "" if not missing else f"missing: {', '.join(missing)}",
    )
    # wontfix is present on every new repo, so its presence proves nothing about the
    # student; its absence means they deleted it and the mapping file now names a
    # label that does not exist.
    for lbl in DEFAULT_LABELS:
        if lbl in names:
            res.add(f"Label {lbl}", None, "GitHub default, present -- not graded")
        else:
            res.add(f"Label {lbl}", False, "deleted? it is named in triage-labels.md")


def check_writeup(res: Result, org: str, handle: str) -> None:
    """Write-up exists, is long enough, and carries pasted --json evidence."""
    repo = f"{org}/flashcards-{handle}"
    try:
        content = gh("api", f"repos/{repo}/contents/{WRITEUP}", "--jq", ".content")
        text = base64.b64decode(content.strip().replace("\n", "")).decode("utf-8", "replace")
    except GhError:
        res.add(f"{WRITEUP} present", False, "not found")
        return

    res.add(f"{WRITEUP} present", True)

    words = len(text.split())
    res.add(
        "Write-up length",
        words >= WRITEUP_MIN_WORDS,
        f"{words} words (need {WRITEUP_MIN_WORDS}+)",
    )

    has_json = '"baseRefName"' in text and '"headRefName"' in text
    res.add(
        "Terminal evidence pasted",
        has_json,
        "" if has_json else "no --json output containing baseRefName and headRefName",
    )

    # Human-graded, but flag whether anything was cited at all.
    cites = any(tok in text for tok in ("#", "gh pr", "gh issue"))
    res.add("Cites artifacts (indicative)", None if cites else False,
            "reads as ungrounded narration" if not cites else "for the human grader")


def check_membership(res: Result, org: str, handle: str) -> None:
    """Public org membership. Only public members are visible to this endpoint."""
    try:
        gh("api", f"orgs/{org}/public_members/{handle}", "--silent")
        res.add("Org membership public", True)
    except GhError:
        res.add(
            "Org membership public",
            False,
            "not a public member (private membership breaks Week 5 - see M01)",
        )


def check_student(org: str, handle: str) -> Result:
    res = Result(handle)
    if check_repo(res, org, handle) is not None:
        check_files(res, org, handle)
        check_labels(res, org, handle)
        check_writeup(res, org, handle)
    check_membership(res, org, handle)
    return res


def render(res: Result) -> None:
    status = f"{RED}FAIL{RESET}" if res.failed else f"{GREEN}PASS{RESET}"
    print(f"\n{res.handle}  [{status}]")
    for name, ok, detail in res.checks:
        if ok is True:
            mark = f"{GREEN}ok  {RESET}"
        elif ok is False:
            mark = f"{RED}fail{RESET}"
        else:
            mark = f"{YELLOW}note{RESET}"
        line = f"  {mark} {name}"
        if detail:
            line += f"  {DIM}{detail}{RESET}"
        print(line)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--org", required=True, help="course GitHub organization")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--handle", help="one student's GitHub handle")
    group.add_argument(
        "--handles", type=Path, help="file with one GitHub handle per line"
    )
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit machine-readable results instead of a report")
    args = parser.parse_args(argv)

    if shutil.which("gh") is None:
        print("gh CLI not found on PATH", file=sys.stderr)
        return 2

    if args.handle:
        handles = [args.handle]
    else:
        handles = [
            line.strip()
            for line in args.handles.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]

    results = [check_student(args.org, h) for h in handles]

    if args.as_json:
        print(json.dumps(
            [
                {
                    "handle": r.handle,
                    "passed": not r.failed,
                    "checks": [
                        {"name": n, "ok": ok, "detail": d} for n, ok, d in r.checks
                    ],
                }
                for r in results
            ],
            indent=2,
        ))
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
