"""Build roadmap.docx from the single task list below.

Run: python roadmap/build_roadmap.py

Edit the Python, never the .docx -- same rule as objectives/build_objectives.py.
Status values are DONE, NEXT, TODO, BLOCKED, DECIDE.
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent

TITLE = "GitHub Pull Requests for Agentic Coders"
SUBTITLE = "Build roadmap"
AS_OF = "2026-09-14"

ACCENT = RGBColor(0x6D, 0x4A, 0xB8)
MUTED = RGBColor(0x66, 0x66, 0x66)

STATUS_COLOR = {
    "DONE": RGBColor(0x1B, 0x7F, 0x3B),
    "NEXT": RGBColor(0x6D, 0x4A, 0xB8),
    "TODO": RGBColor(0x44, 0x44, 0x44),
    "BLOCKED": RGBColor(0xB3, 0x2D, 0x2D),
    "DECIDE": RGBColor(0xA5, 0x6A, 0x00),
}

INTRO = (
    "What is built, what is not, and what has to be decided before a cohort can run. "
    "Generated from roadmap/build_roadmap.py -- edit the script, not this document. "
    "The authoritative detail lives in NOTES.md (verified facts, open questions, build "
    "log); this is the map above it."
)

# (section, blurb, [(status, item, detail)])
SECTIONS = [
    (
        "Done",
        "Shipped and verified against real GitHub, not asserted.",
        [
            ("DONE", "Course backbone",
             "MISSION.md, CONTEXT.md, NOTES.md, RESOURCES.md, ADRs 0001-0004, and the "
             "M01-M36 mastery-objectives workbook with its generator."),
            ("DONE", "Week 1 vertical slice",
             "Course Home, the Week 1 hub, thirteen Learning Pages across M01-M06 (one "
             "folder per objective: an index.html entry page plus supporting pages, each "
             "with a Self-Check, a flashcard deck, and a where-to-learn-more list), "
             "assignment A1 with its rubric, and two checkers. Every terminal transcript "
             "was captured from a real command run against a real repository."),
            ("DONE", "Seed Repo: perro-ruidoso/flashcards-seed",
             "Public, template flag set, CI green in 24s on Python 3.12. Tracer bullet "
             "only -- Card/Deck, json_store, `flashcards list` -- so the backlog is "
             "genuinely open work. 20 tests, ruff and mypy --strict clean, zero runtime "
             "dependencies."),
            ("DONE", "Seed Repo backlog",
             "15 issues, 19 blocking edges recorded as real GitHub issue dependencies. "
             "Graph re-derived from what GitHub stores: 5 waves, max parallel width 4, "
             "five two-parent joins -- matches the spec's answer key."),
            ("DONE", "Course repo under version control",
             "perro-ruidoso/gh-pr-mastery is public, with the site live at "
             "perro-ruidoso.github.io/gh-pr-mastery from main /docs. Dogfooded: seven "
             "merged PRs as of 2026-09-13, each closing its issue by keyword within two "
             "seconds, two recorded blocking relations (#2 by #1, #13 by #11), and one "
             "stacked PR (#14) retargeted to main after its parent merged -- now M06's "
             "second worked example. A1 item 6 has a real exhibit."),
            ("DONE", "Weeks 1-2 audit (issue #15, 2026-09-13)",
             "With the tools live, not from memory: 90 source URLs re-fetched and every "
             "quotation re-checked (3 more docs.github.com redirects, 1 rewritten "
             "sentence); every gh transcript re-run on the installed 2.100.0 (cli/cli#14398 "
             "had closed unmerged; M06's course-repo snapshot was two PRs and one edge "
             "stale); check_site.py fault-injected 25/25 and one regex fixed; check_a1/a2 "
             "fault-injected on the throwaway Instance, every reachable rule caught; all "
             "28 pages render-tested at 1200 and 400 px (one overflow fixed); 81 of 93 "
             "self-check questions rewritten so option length no longer gives the answer "
             "away."),
            ("DONE", "Weeks 1-3 audit (issue #19, 2026-09-14)",
             "Extended to Week 3 plus a cross-week pass: 105 URLs re-fetched (all 200, no "
             "redirects), 621 quotations re-checked, every read-only gh transcript re-run "
             "(cli/cli moved again; M06's course-repo snapshot was a day stale), the "
             "installed skills re-diffed against upstream and the plugin manifest (the "
             "plugin has 25 skills and lacks request-refactor-plan, qa, git-guardrails; "
             "ask-matt reversed its handoff/compact advice), nine links dead on the "
             "published site fixed and a check_site.py rule added (28/28 faults caught), "
             "check_a3 16/16 by snapshot replay, check_a1/a2 22/22 by live mutation, 42 "
             "pages render-tested at 1200 and 400 px, 133 self-checks with 0 flagged. "
             "Three decisions owed (below)."),
        ],
    ),
    (
        "Next",
        "The recommended order. Weeks 1-3 are shipped (1-2 audited); "
        "the upstream repo is not needed until Week 5.",
        [
            ("DONE", "Week 2 -- M07 to M12",
             "Week 2 hub plus twelve Learning Pages (two per objective), assignment A2 "
             "with its rubric, and check_a2.py. Transcripts captured with gh 2.100.0 "
             "(now the installed version) against the Seed Repo and a throwaway "
             "Instance; the two-parent sub-issue experiment and the accepted dependency "
             "cycle are on the M11 pages. M12's Linear UI steps are quoted from the docs "
             "and marked as not run live. Audited 2026-09-13 (see Done)."),
            ("DONE", "Week 3 -- M13 to M18",
             "Week 3 hub plus fourteen Learning Pages (two per objective, three for "
             "M16), assignment A3 with its rubric, and check_a3.py. Built by doing the "
             "week on a throwaway Instance (flashcards-w3probe, 2026-09-13): gh issue "
             "develop branches, a stacked PR whose closing keyword was ignored until "
             "retargeted, the diff growing after a squash and shrinking after a rebase, "
             "a deliberate drive-by PR split into a clean one, a genuine two-file "
             "conflict resolved by running /resolving-merge-conflicts, and two probes "
             "showing --delete-branch closes a stacked child while the auto-delete "
             "setting retargets it. Checker fault-injected 13/13; 42 pages render-tested "
             "headless at 1200 and 400 px; 0 of 40 self-check questions flagged."),
            ("NEXT", "Weeks 4 to 6 -- M19 to M36",
             "Three more vertical slices, ~18 Learning Pages, assignments A4-A6, two "
             "graded concept quizzes, and the capstone."),
            ("TODO", "Upstream Repo: flashcards-upstream",
             "The shared repo students contribute to and take turns maintaining. Needed "
             "by Week 5. Two modes, and the difference is taught rather than hidden -- "
             "see adr/0004."),
        ],
    ),
    (
        "Infrastructure",
        "Course machinery that is not a Learning Page.",
        [
            ("TODO", "Claude GitHub Action on the upstream repo",
             "Workflow plus a CLAUDE_CODE_OAUTH_TOKEN repository secret from "
             "`claude setup-token`. Tied to the instructor's personal subscription: a "
             "single point of failure to monitor."),
            ("BLOCKED", "Week 4 planted-bug diff",
             "The three SM-2 bugs live in scheduler.py, which is ticket T03's output. "
             "The diff can only be authored on an Instance where T03 has landed, never "
             "against the template. Also still open: whether it ships as a prepared PR "
             "per Instance or as a patch."),
            ("TODO", "Merge-strategy simulator widget",
             "The one bespoke widget, for Week 5. Vanilla JS, vendored, per adr/0001."),
            ("TODO", "UI captures",
             "Rulesets, merge queue configuration, and Linear settings -- the surfaces "
             "with no CLI equivalent. Stored under docs/assets/shots/ with visible "
             "capture dates, because they rot."),
            ("TODO", "Exercise the checkers' --handles batch mode once per cohort",
             "All three checkers accept --handles FILE and --json; no audit has run the "
             "batch path. A three-line file (seed, w2probe, a nonexistent handle) catches a "
             "loop or exit-code regression before grading night. Twenty minutes."),
            ("TODO", "Part 7 live-demo scripts for Weeks 2 and 3",
             "Week 1 has scripted demos with real output; Weeks 2-3 have Part 10 bullets. "
             "The Week 3 pages already hold every command and output (the retarget, the "
             "conflict); Week 2's is the M11 two-parent experiment. Two hours, with Week 4."),
            ("TODO", "Delete the throwaway Instances flashcards-w2probe and flashcards-w3probe",
             "Both private, in the org (still there 2026-09-14; w2probe now also carries the 2026-09-14 audit's fault-injection commits and a ninth closed issue). w2probe carried the M08/M11/M12 transcripts and "
             "the 2026-09-13 checker fault-injection; w3probe carried every Week 3 "
             "transcript (issues #1-#3, PRs #4-#11) and the check_a3.py run. The build "
             "token lacks delete_repo: `gh auth refresh -s delete_repo && gh repo "
             "delete perro-ruidoso/flashcards-w2probe --yes` and the same for w3probe. "
             "Nothing on the pages needs either."),
            ("TODO", "Linear branch-name linking, live",
             "M13 page 2 quotes Linear's rule that a branch name containing the issue "
             "ID links the PR; not yet observed in a live workspace. Fold into the "
             "Issues Sync live check."),
            ("TODO", "Student roster tooling",
             "handles.txt and a batch run of check_a1.py across the cohort."),
            ("DONE", "check_a1.py grades four labels and notes wontfix",
             "Follows from the triage-label decision. The item now reads 'Triage "
             "labels (4 created + 1 default)', wontfix is a note unless deleted, and "
             "gh label list is retried over ~9 s to cover propagation lag. Exercised "
             "against flashcards-seed and a nonexistent repo."),
            ("TODO", "Confirm Issues Sync live in a Free Linear workspace",
             "Settings > Integrations > GitHub > GitHub Issues shows the + to link a "
             "repo. M12 is written and says on the page that this has not been done; "
             "run the M12 verification protocol once in the instructor workspace and "
             "add dated captures under docs/assets/shots/."),
        ],
    ),
    (
        "Decisions",
        "Three were made on 2026-09-13; one is still owed. The reasoning is in NOTES.md.",
        [
            ("DONE", "Org plan: stay on Team for now",
             "Decided 2026-09-13. Re-checked: still Team, 2 seats, 1 filled. Nothing in "
             "the curriculum depends on the tier, so the consequence is operational: "
             "seats must be bought before inviting (see below). Downgrading to Free "
             "remains the recommendation to revisit before cohort 2."),
            ("DONE", "The fifth triage label is free: accepted",
             "Decided 2026-09-13. wontfix is a GitHub default, so A1 item 4 assesses "
             "four labels, not five, and the checker and A1 now say so. Renaming the "
             "role would fork the Pocock skill's vocabulary; asserting an edit would "
             "grade a colour change, not understanding."),
            ("DONE", "Linear Free includes GitHub Issues Sync",
             "Decided 2026-09-13 on the evidence of linear.app/pricing: Issue sync is a "
             "Core feature on every plan; the docs gate only GitHub Enterprise Cloud "
             "and AI magic-word enrichment. Free caps at 2 teams and 250 issues, ample "
             "for one Instance. M12 is written on the Free assumption; one live check "
             "remains under Infrastructure."),
            ("DECIDE", "Pin the skill set, or track the plugin?",
             "Found 2026-09-14: the handout installs the Claude Code plugin (25 skills, "
             "tracking upstream), the course machine runs a 2026-07-09 snapshot (38). Two of "
             "M18's six named skills and M24's /qa are not in the plugin, and the plugin's "
             "ask-matt gives the opposite handoff/compact advice. Recommendation: track the "
             "plugin and swap the absent skills (NOTES.md, Weeks 1-3 audit, S1)."),
            ("DECIDE", "Replace request-refactor-plan in M18",
             "Its upstream changeset names /to-spec + /improve-codebase-architecture as the "
             "replacement. Recommendation: improve-codebase-architecture (in the plugin, on "
             "ask-matt's map). Touches M18 p2, the objective row, A3 item 6, check_a3.py."),
            ("DECIDE", "Name M24's skill before Week 4 is built",
             "/qa was retired upstream 2026-08-05 into /triage and /to-tickets. One objective "
             "row and one primary source now; a page rewrite if left until later."),
            ("DECIDE", "Does a Pro subscription absorb the cohort's CI review volume?",
             "Or is Max needed? Measure during the Week 5 dry run, before it matters."),
        ],
    ),
    (
        "Before the first cohort",
        "Operational, once the content exists.",
        [
            ("TODO", "Syllabus states that all student work is world-readable",
             "Required by adr/0003 before enrolment, not after."),
            ("TODO", "Buy Team seats for the cohort",
             "The org has 2 seats and stays on Team; a cohort of 8-14 plus the "
             "instructor needs 9-15. Settings > Billing and licensing, then confirm "
             "with gh api orgs/perro-ruidoso --jq .plan. Invitations beyond the seat "
             "count will not go through."),
            ("TODO", "Invite students; each sets org membership to Public",
             "Private membership silently breaks the Claude GitHub App's write-access "
             "detection in Week 5."),
            ("TODO", "Re-verify every vendor-behaviour fact in NOTES.md",
             "Those are the rows that move. Re-check before each cohort, not once."),
            ("TODO", "Week 5 dry run",
             "The first time gates, merge queue, and agentic CI review run together "
             "under load."),
        ],
    ),
]


def _shade(cell, hex_fill):
    """python-docx has no cell-shading API; drop to the underlying XML."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_fill)
    cell._tc.get_or_add_tcPr().append(shd)


def build(path: Path) -> None:
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)

    for section in doc.sections:
        section.left_margin = section.right_margin = Inches(0.9)
        section.top_margin = section.bottom_margin = Inches(0.8)

    title = doc.add_paragraph()
    run = title.add_run(TITLE)
    run.font.size = Pt(21)
    run.font.bold = True
    run.font.color.rgb = ACCENT
    title.paragraph_format.space_after = Pt(0)

    sub = doc.add_paragraph()
    run = sub.add_run(f"{SUBTITLE}  ·  as of {AS_OF}")
    run.font.size = Pt(11)
    run.font.color.rgb = MUTED
    sub.paragraph_format.space_after = Pt(10)

    intro = doc.add_paragraph(INTRO)
    intro.paragraph_format.space_after = Pt(14)

    counts: dict[str, int] = {}
    for _, _, items in SECTIONS:
        for status, _, _ in items:
            counts[status] = counts.get(status, 0) + 1

    legend = doc.add_paragraph()
    for i, key in enumerate(["DONE", "NEXT", "TODO", "BLOCKED", "DECIDE"]):
        if key not in counts:
            continue
        if i:
            legend.add_run("    ")
        run = legend.add_run(f"{key} {counts[key]}")
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = STATUS_COLOR[key]
    legend.paragraph_format.space_after = Pt(16)

    for name, blurb, items in SECTIONS:
        head = doc.add_paragraph()
        run = head.add_run(name)
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = ACCENT
        head.paragraph_format.space_before = Pt(12)
        head.paragraph_format.space_after = Pt(2)

        note = doc.add_paragraph()
        run = note.add_run(blurb)
        run.font.size = Pt(9.5)
        run.font.italic = True
        run.font.color.rgb = MUTED
        note.paragraph_format.space_after = Pt(8)

        table = doc.add_table(rows=0, cols=2)
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        table.autofit = False

        for status, item, detail in items:
            row = table.add_row()
            row.cells[0].width = Inches(0.85)
            row.cells[1].width = Inches(5.85)

            para = row.cells[0].paragraphs[0]
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = para.add_run(status)
            run.font.bold = True
            run.font.size = Pt(8)
            run.font.color.rgb = STATUS_COLOR[status]
            _shade(row.cells[0], "F4F2F9")

            cell = row.cells[1]
            first = cell.paragraphs[0]
            run = first.add_run(item)
            run.font.bold = True
            run.font.size = Pt(10.5)
            first.paragraph_format.space_after = Pt(1)

            body = cell.add_paragraph()
            run = body.add_run(detail)
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
            body.paragraph_format.space_after = Pt(0)

    doc.add_paragraph()
    foot = doc.add_paragraph()
    run = foot.add_run(
        "Regenerate with: python roadmap/build_roadmap.py   ·   "
        "Detail and sources: NOTES.md"
    )
    run.font.size = Pt(8.5)
    run.font.color.rgb = MUTED

    doc.save(path)


if __name__ == "__main__":
    known = set(STATUS_COLOR)
    for name, _, items in SECTIONS:
        for status, item, _ in items:
            assert status in known, f"{item}: unknown status {status!r}"
    total = sum(len(items) for _, _, items in SECTIONS)
    out = HERE / "roadmap.docx"
    build(out)
    print(f"wrote {total} items across {len(SECTIONS)} sections to {out.name}")
