"""Validate the course site: internal links, assets, and per-page structure.

    python checkers/check_site.py

Catches the failures that are invisible until a student hits them - a lesson linking to a
page that does not exist, a page that uses a Mermaid diagram without loading Mermaid, a
self-check whose data-answer names an option that is not there, a flashcard with no back,
an objective folder whose pages do not all link each other, an Apply, Create, or Evaluate
page with no hands-on checklist, two decks sharing a localStorage id, a Week Hub the Course Home does
not link, a relative link that leaves docs/ and so 404s on the published site, a closing tag
that matches nothing (browsers swallow it silently).

Layout it expects: docs/week-NN/index.html is the Week Hub; docs/week-NN/mNN-slug/ is one
objective, holding index.html (the entry Learning Page) plus any supporting pages.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

HREF = re.compile(r'href="([^"]+)"')
SRC = re.compile(r'src="([^"]+)"')
QUESTION = re.compile(r'<div class="q" data-answer="([a-z])">(.*?)</div>\s*</div>', re.S)
OPTION = re.compile(r'data-opt="([a-z])"')
CARD = re.compile(r'<div class="fc">(.*?)</div>\s*</div>', re.S)
# A face is present if something other than its own closing tag follows the opening tag.
CARD_FRONT = re.compile(r'<div class="fc-front">(?!\s*</div>)\s*\S')
CARD_BACK = re.compile(r'<div class="fc-back">(?!\s*</div>)\s*\S')
DECK_ID = re.compile(r'data-deck="([^"]+)"')
BLOOM = re.compile(r'Bloom:\s*(Understand|Apply|Analyze|Evaluate|Create)')

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
            rel = path.relative_to(ROOT)
            if not resolved.exists():
                problems.append(f"{rel}: broken link -> {raw}")
            elif not resolved.is_relative_to(DOCS):
                # Resolves on disk, but GitHub Pages serves docs/ alone, so on the
                # published site this is a 404 (found 2026-09-14: nine links to
                # assignments/, adr/, and CONTEXT.md). Link the GitHub blob URL instead.
                problems.append(f"{rel}: link escapes docs/ (dead on the published site) -> {raw}")
    return checked


VOID = {"meta", "link", "br", "img", "input", "hr", "source", "wbr"}


class TagBalance(HTMLParser):
    """Report a closing tag that does not match the innermost open element - the stray
    `</tt>` that a Week 4 page shipped with, which browsers swallow and nothing else saw."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, int]] = []
        self.problems: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            opened = self.stack[-1][0] if self.stack else "nothing"
            self.problems.append(f"line {self.getpos()[0]}: </{tag}> closes {opened}")
            # Recover so one slip does not cascade into a hundred reports.
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break
            return
        self.stack.pop()


def check_markup(path: Path, html: str, problems: list[str]) -> None:
    parser = TagBalance()
    parser.feed(html)
    parser.close()
    rel = path.relative_to(ROOT)
    for msg in parser.problems[:5]:
        problems.append(f"{rel}: mismatched tag, {msg}")
    for tag, line in parser.stack:
        if tag not in ("html", "body"):
            problems.append(f"{rel}: <{tag}> opened at line {line} is never closed")


def is_lesson_page(path: Path) -> bool:
    """A Learning Page lives in an objective folder: docs/week-NN/mNN-slug/*.html."""
    return (path.parent.name.startswith("m")
            and path.parent.parent.name.startswith("week-")
            and path.suffix == ".html")


def check_structure(path: Path, html: str, problems: list[str]) -> None:
    rel = path.relative_to(ROOT)
    is_lesson = is_lesson_page(path)

    if "<title>" not in html:
        problems.append(f"{rel}: no <title>")
    depth = len(path.relative_to(DOCS).parts) - 1
    expected_css = 'href="' + "../" * depth + 'assets/styles.css"'
    if expected_css not in html:
        problems.append(f"{rel}: stylesheet not linked as {expected_css}")

    # A page that renders Mermaid must also load it.
    if 'class="mermaid"' in html and "mermaid.min.js" not in html:
        problems.append(f"{rel}: uses pre.mermaid but never loads mermaid.min.js")
    if "mermaid.min.js" in html and 'class="mermaid"' not in html:
        problems.append(f"{rel}: loads mermaid.min.js but has no diagram")

    if is_lesson:
        for required, label in (
            ('class="obj-banner"', "objective banner"),
            ('class="pagemap"', "objective page map"),
            ('class="selfcheck"', "self-check"),
            ('class="flashcards"', "flashcard deck"),
            ('class="callout ask"', "ask-your-teacher callout"),
            ('class="learnmore"', "where-to-learn-more section"),
            ('class="sources"', "sources section"),
            ('class="pager"', "pager"),
        ):
            if required not in html:
                problems.append(f"{rel}: missing {label}")
        # An objective a student *does* or *judges* needs a checklist; a concept page
        # (Understand, Analyze) does not.
        bloom = BLOOM.search(html)
        if bloom and bloom.group(1) in ("Apply", "Create", "Evaluate") and 'class="handson"' not in html:
            problems.append(f"{rel}: Bloom {bloom.group(1)} page has no hands-on checklist")

    # A page with a flashcard deck must load the component, and every card
    # needs a non-empty front and back.
    if 'class="flashcards"' in html and "flashcards.js" not in html:
        problems.append(f"{rel}: has a flashcard deck but never loads flashcards.js")
    if "flashcards.js" in html and 'class="flashcards"' not in html:
        problems.append(f"{rel}: loads flashcards.js but has no deck")
    for i, card in enumerate(CARD.findall(html), start=1):
        if not CARD_FRONT.search(card):
            problems.append(f"{rel}: flashcard {i} has no front")
        if not CARD_BACK.search(card):
            problems.append(f"{rel}: flashcard {i} has no back")
    if 'class="flashcards"' in html and 'data-deck="' not in html:
        problems.append(f"{rel}: flashcard deck has no data-deck id")

    # Every self-check answer must name an option that exists on that question.
    for answer, block in QUESTION.findall(html):
        opts = set(OPTION.findall(block))
        if not opts:
            continue
        if answer not in opts:
            problems.append(
                f"{rel}: self-check data-answer='{answer}' but options are {sorted(opts)}"
            )


def check_site_wiring(found: list[Path], problems: list[str]) -> None:
    """Deck ids are unique across the site (they key localStorage), and the Course Home
    links every Week Hub that exists."""
    seen: dict[str, Path] = {}
    for path in found:
        for deck in DECK_ID.findall(path.read_text(encoding="utf-8")):
            if deck in seen:
                problems.append(
                    f"{path.relative_to(ROOT)}: deck id {deck!r} also used by {seen[deck].relative_to(ROOT)}"
                )
            seen.setdefault(deck, path)
    home = DOCS / "index.html"
    if home.exists():
        home_html = home.read_text(encoding="utf-8")
        for hub in sorted(DOCS.glob("week-*/index.html")):
            link = f'href="{hub.parent.name}/index.html"'
            if link not in home_html:
                problems.append(f"docs/index.html: does not link {hub.parent.name}/index.html")


def check_objective_coverage(problems: list[str]) -> None:
    """Every objective folder is reachable from its week hub, has an index.html, and its
    pages all link each other through the page map."""
    for hub in sorted(DOCS.glob("week-*/index.html")):
        hub_html = hub.read_text(encoding="utf-8")
        for folder in sorted(d for d in hub.parent.iterdir() if d.is_dir() and d.name.startswith("m")):
            frel = folder.relative_to(ROOT)
            pages = sorted(folder.glob("*.html"))
            if not (folder / "index.html").exists():
                problems.append(f"{frel}: objective folder has no index.html")
            for page in pages:
                if f"{folder.name}/{page.name}" not in hub_html:
                    problems.append(f"{hub.relative_to(ROOT)}: does not link {folder.name}/{page.name}")
            for page in pages:
                html = page.read_text(encoding="utf-8")
                for sibling in pages:
                    if sibling == page:
                        continue
                    if f'href="{sibling.name}"' not in html:
                        problems.append(
                            f"{page.relative_to(ROOT)}: page map does not link sibling {sibling.name}"
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
        check_markup(path, html, problems)

    check_objective_coverage(problems)
    check_site_wiring(found, problems)

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
