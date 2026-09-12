"""Validate the course site: internal links, assets, and per-page structure.

    python checkers/check_site.py

Catches the failures that are invisible until a student hits them - a lesson linking to a
page that does not exist, a page that uses a Mermaid diagram without loading Mermaid, a
self-check whose data-answer names an option that is not there.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urldefrag

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

HREF = re.compile(r'href="([^"]+)"')
SRC = re.compile(r'src="([^"]+)"')
QUESTION = re.compile(r'<div class="q" data-answer="([a-z])">(.*?)</div>\s*</div>', re.S)
OPTION = re.compile(r'data-opt="([a-z])"')

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


def pages() -> list[Path]:
    return sorted(DOCS.rglob("*.html"))


def check_links(path: Path, html: str, problems: list[str]) -> int:
    checked = 0
    for attr in (HREF, SRC):
        for raw in attr.findall(html):
            if raw.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target, _ = urldefrag(unquote(raw))
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            checked += 1
            if not resolved.exists():
                rel = path.relative_to(ROOT)
                problems.append(f"{rel}: broken link -> {raw}")
    return checked


def check_structure(path: Path, html: str, problems: list[str]) -> None:
    rel = path.relative_to(ROOT)
    is_lesson = path.name.startswith("m") and path.parent.name.startswith("week-")

    if "<title>" not in html:
        problems.append(f"{rel}: no <title>")
    if 'href="../assets/styles.css"' not in html and 'href="assets/styles.css"' not in html:
        problems.append(f"{rel}: stylesheet not linked")

    # A page that renders Mermaid must also load it.
    if 'class="mermaid"' in html and "mermaid.min.js" not in html:
        problems.append(f"{rel}: uses pre.mermaid but never loads mermaid.min.js")
    if "mermaid.min.js" in html and 'class="mermaid"' not in html:
        problems.append(f"{rel}: loads mermaid.min.js but has no diagram")

    if is_lesson:
        for required, label in (
            ('class="obj-banner"', "objective banner"),
            ('class="selfcheck"', "self-check"),
            ('class="sources"', "sources section"),
            ('class="pager"', "pager"),
        ):
            if required not in html:
                problems.append(f"{rel}: missing {label}")

    # Every self-check answer must name an option that exists on that question.
    for answer, block in QUESTION.findall(html):
        opts = set(OPTION.findall(block))
        if not opts:
            continue
        if answer not in opts:
            problems.append(
                f"{rel}: self-check data-answer='{answer}' but options are {sorted(opts)}"
            )


def check_objective_coverage(problems: list[str]) -> None:
    """Every objective with a learning page should be reachable from its week hub."""
    for hub in sorted(DOCS.glob("week-*/index.html")):
        html = hub.read_text(encoding="utf-8")
        for lesson in sorted(hub.parent.glob("m*.html")):
            if lesson.name not in html:
                problems.append(
                    f"{hub.relative_to(ROOT)}: does not link {lesson.name}"
                )


def main() -> int:
    if not DOCS.exists():
        print(f"no docs/ directory at {DOCS}", file=sys.stderr)
        return 2

    problems: list[str] = []
    links = 0
    found = pages()

    for path in found:
        html = path.read_text(encoding="utf-8")
        links += check_links(path, html, problems)
        check_structure(path, html, problems)

    check_objective_coverage(problems)

    print(f"{len(found)} pages, {links} internal links checked")
    if problems:
        print(f"\n{RED}{len(problems)} problem(s):{RESET}")
        for p in problems:
            print(f"  {RED}x{RESET} {p}")
        return 1

    print(f"{GREEN}all checks passed{RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
