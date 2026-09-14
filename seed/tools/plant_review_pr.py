"""Open the Week 4 review-drill pull request on an Instance.

    python seed/tools/plant_review_pr.py --repo perro-ruidoso/flashcards-<handle>
    python seed/tools/plant_review_pr.py --repo OWNER/REPO --dry-run

Files the SM-2 scheduler ticket from `seed/planted/ticket.md`, creates a branch for it
with `gh issue develop`, adds `seed/planted/scheduler.py` and `test_scheduler.py` as the
ticket's implementation, and opens a pull request with `seed/planted/pr-body.md`. The
implementation carries the three defects `seed/SPEC.md` section 7 describes, and the
tests pass anyway - that is the point. **Run this as the student who owns the Instance**,
so the student is the PR's author: GitHub refuses an author's own APPROVE and
REQUEST_CHANGES (verified 2026-09-14), which is what makes the peer the reviewer and the
student the one who answers review (M23).

Refuses to run if the Instance already has a `src/flashcards/domain/scheduler.py`; the
instructor guide says what to do then. Works in a temporary clone and leaves the
working directory alone. Needs an authenticated `gh` (2.94.0+) and `git`.

Decision record: `seed/SPEC.md` section 10 (prepared PR, opened by the student) and
`NOTES.md`, Week 4.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLANTED = HERE.parent / "planted"
TITLE = "SM-2 scheduler: next interval and ease update"
TARGETS = {
    "scheduler.py": Path("src/flashcards/domain/scheduler.py"),
    "test_scheduler.py": Path("tests/domain/test_scheduler.py"),
}


def run(*args: str, cwd: Path | None = None, check: bool = True) -> str:
    proc = subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if check and proc.returncode != 0:
        sys.exit(f"{' '.join(args)}\n{proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, help="OWNER/REPO of the Instance")
    parser.add_argument("--dry-run", action="store_true", help="print the steps, change nothing")
    args = parser.parse_args(argv)

    if shutil.which("gh") is None or shutil.which("git") is None:
        sys.exit("needs gh and git on PATH")
    for name in TARGETS:
        if not (PLANTED / name).exists():
            sys.exit(f"missing {PLANTED / name}")

    existing = subprocess.run(
        ["gh", "api", f"repos/{args.repo}/contents/{TARGETS['scheduler.py'].as_posix()}"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if existing.returncode == 0:
        sys.exit(
            f"{args.repo} already has {TARGETS['scheduler.py']}; this drill adds the module. "
            "See the instructor guide, Week 4, for the variant to use."
        )

    steps = [
        f"gh issue create -R {args.repo} --title {TITLE!r} --body-file seed/planted/ticket.md",
        "gh repo clone (temporary)",
        "gh issue develop <N> --name <N>-sm2-scheduler --checkout",
        "copy seed/planted/scheduler.py and test_scheduler.py into place; git commit; git push",
        "gh pr create --body-file seed/planted/pr-body.md (Closes #<N>)",
    ]
    if args.dry_run:
        print("\n".join(steps))
        return 0

    issue_url = run("gh", "issue", "create", "-R", args.repo, "--title", TITLE,
                    "--body-file", str(PLANTED / "ticket.md"))
    number = issue_url.rstrip("/").rsplit("/", 1)[-1]
    print(f"ticket: {issue_url}")

    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "instance"
        run("gh", "repo", "clone", args.repo, str(clone), "--", "--quiet")
        branch = f"{number}-sm2-scheduler"
        run("gh", "issue", "develop", number, "--name", branch, "--checkout", cwd=clone)
        for name, target in TARGETS.items():
            (clone / target).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PLANTED / name, clone / target)
        run("git", "add", "-A", cwd=clone)
        message = (
            f"{TITLE}\n\nOne function, two constants, one test per rule, per docs/adr/0001.\n\n"
            f"Closes #{number}\n"
        )
        proc = subprocess.run(["git", "commit", "-q", "-F", "-"], cwd=clone, input=message,
                              capture_output=True, text=True, encoding="utf-8")
        if proc.returncode != 0:
            sys.exit(proc.stderr.strip())
        run("git", "push", "-q", "-u", "origin", branch, cwd=clone)
        body = (PLANTED / "pr-body.md").read_text(encoding="utf-8").replace("#ISSUE", f"#{number}")
        body_file = Path(tmp) / "pr-body.md"
        body_file.write_text(body, encoding="utf-8")
        pr_url = run("gh", "pr", "create", "--title", TITLE, "--body-file", str(body_file), cwd=clone)
        print(f"pull request: {pr_url}")
        print(f"branch: {branch}  (from issue #{number})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
