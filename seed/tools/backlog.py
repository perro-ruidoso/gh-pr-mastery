"""The 15-ticket backlog for flashcards-seed, from seed/SPEC.md section 6.

Single source of truth for both the topological check and issue creation.
"""

# id -> (title, layer, blocked_by, context, acceptance, out_of_scope)
TICKETS = {
    "T01": (
        "Add review state to Card: repetitions, ease factor, interval, due date",
        "domain",
        [],
        "A Card today knows its prompt and its answer and nothing about when it should "
        "next be seen. Every scheduling ticket in this backlog needs somewhere to put "
        "that state, so it goes on the Card first.",
        [
            "`Card` carries `repetitions: int`, `ease_factor: float`, `interval: int`, "
            "and `due: date | None`",
            "Defaults for a never-reviewed card are `0`, `2.5`, `0`, `None` - the "
            "starting ease factor is fixed in `docs/adr/0001`",
            "`Card` stays frozen and stays free of I/O",
            "`tests/domain/test_models.py` pins the defaults, and pins that the new "
            "fields are optional so existing call sites still construct a Card with "
            "three arguments",
        ],
        "Persistence (T02), any arithmetic that changes these fields (T03), and any "
        "command that displays them.",
    ),
    "T02": (
        "Persist review state in the deck file",
        "storage",
        ["T01"],
        "T01 puts review state on the Card in memory, where it is lost the moment the "
        "process exits. The deck file has to carry it or nothing else in this backlog "
        "is observable across runs.",
        [
            "`save_deck` writes the four review fields for every card",
            "`load_deck` reads them, and a deck file written before this change still "
            "loads - missing fields fall back to the T01 defaults",
            "`due` round-trips as an ISO date string, or `null`",
            "`tests/storage/test_json_store.py` covers the round trip, the old-file "
            "fallback, and a malformed date",
        ],
        "Changing the file format's top-level shape, and any schema versioning scheme.",
    ),
    "T03": (
        "SM-2 scheduler: next interval and ease update",
        "domain",
        ["T01"],
        "This is the heart of the application: given a card's current review state and "
        "the learner's grade, decide when the card is next due. It is specified "
        "completely in `docs/adr/0001-sm2-rounding-and-the-clock.md`; implement that, "
        "not something like it.",
        [
            "New module `src/flashcards/domain/scheduler.py`, importing nothing from "
            "`storage/` or `cli/`",
            "`review(card, grade, today)` returns a **new** Card - it never mutates and "
            "never reads the clock",
            "Intervals follow `I(1)=1`, `I(2)=6`, `I(n)=I(n-1)*EF`, rounded **half-up** "
            "with a floor of 1 day; bare `round()` is wrong and `docs/adr/0001` says why",
            "The ease factor update is applied first and the 1.3 floor after",
            "A grade below 3 resets the repetition count and **leaves the ease factor "
            "unchanged**",
            "A grade outside 0-5 raises `ValueError`",
            "`tests/domain/test_scheduler.py` covers each rule above by name, including "
            "a fail-then-recover sequence and an exact-half interval",
        ],
        "Choosing which cards to review (T05), and anything that reads or writes a file.",
    ),
    "T04": (
        "`review` command: one card, prompt, grade, schedule",
        "cli",
        ["T02", "T03"],
        "The first ticket that closes the loop: show a card, take a grade, schedule it, "
        "and save. Until this exists the scheduler is unreachable from the outside.",
        [
            "`flashcards review --deck <path>` shows one card's front, waits, reveals "
            "the back, and reads a grade of 0-5",
            "The graded card is rescheduled through `domain.scheduler` and the deck is "
            "saved",
            "`today` is obtained once, in `cli/`, and passed down - no layer below reads "
            "the clock",
            "An invalid grade re-prompts rather than crashing",
            "`tests/cli/test_main.py` drives the command with scripted stdin and a fixed "
            "`today`, and asserts the saved deck",
        ],
        "Choosing *which* card - T05 does due-filtering, and until then the command "
        "takes the first card. Limits (T06) and tags (T10).",
    ),
    "T05": (
        "Due-date filtering: select only cards due today",
        "domain",
        ["T03"],
        "A review session should offer the cards that are actually due, not the whole "
        "deck. That selection is a pure function of a deck and a date, so it belongs in "
        "the domain layer next to the scheduler.",
        [
            "A function taking a deck and `today` and returning the due cards, oldest "
            "due date first",
            "A card that has never been reviewed (`due is None`) counts as due",
            "A card due today counts as due; one due tomorrow does not",
            "Ties break on the card's position in the deck, so the order is deterministic",
            "Tests cover never-reviewed, due-today, overdue, and not-yet-due",
        ],
        "Wiring it into the `review` command - that is part of T06.",
    ),
    "T06": (
        "`review --limit N`",
        "cli",
        ["T04", "T05"],
        "A session should end after a fixed number of cards rather than running to the "
        "end of the deck. This is also where `review` starts drawing from the due list "
        "built in T05 instead of taking whatever comes first.",
        [
            "`flashcards review --limit N` reviews at most N cards, drawn from T05's due "
            "list in its order",
            "Without `--limit`, every due card is offered",
            "`--limit 0` is a usage error; a limit larger than the due count reviews "
            "what is there and says so",
            "The deck is saved once, after the session, not once per card",
            "Tests cover a limit below, equal to, and above the number of due cards",
        ],
        "Tag filtering (T10) and any session summary output (T12).",
    ),
    "T07": (
        "Tag field on Card",
        "domain",
        ["T01"],
        "Decks grow past the point where reviewing all of them together is useful. Tags "
        "are the grouping mechanism; this ticket adds the field and nothing else.",
        [
            "`Card` carries `tags: tuple[str, ...]`, defaulting to empty",
            "Tags are normalised to lowercase and de-duplicated, order preserved",
            "An empty-string tag is rejected with `ValueError`",
            "`Card` stays frozen, which is why tags are a tuple rather than a list",
            "Tests pin normalisation, de-duplication, and the empty-tag rejection",
        ],
        "Persisting tags (T08), and any command that reads or writes them.",
    ),
    "T08": (
        "Tag persistence in the deck file",
        "storage",
        ["T07", "T02"],
        "Tags exist in memory after T07, and review state persists after T02. This "
        "ticket makes tags survive a save/load cycle too, on the same file format.",
        [
            "`save_deck` writes a `tags` array for every card",
            "`load_deck` reads it, and a deck file with no `tags` key loads as an "
            "untagged deck",
            "Loading applies the same normalisation T07 defined - a file holding "
            "`[\"Verb\", \"verb\"]` yields one tag",
            "`tests/storage/test_json_store.py` covers the round trip and the "
            "missing-key fallback",
        ],
        "Any command-line surface for tags (T09, T10, T13).",
    ),
    "T09": (
        "`add` command with `--tags`",
        "cli",
        ["T08"],
        "Every card in a deck so far had to be written into the JSON file by hand. This "
        "is the first command that creates one, and the first surface where a user "
        "supplies tags.",
        [
            "`flashcards add --deck <path> --front F --back B [--tags a,b]` appends a "
            "card and saves",
            "The card id is generated and is unique within the deck",
            "A duplicate `--front` in the same deck is a warning, not an error",
            "Tags are split on commas and normalised by the domain layer, not by `cli/`",
            "Tests cover a plain add, an add with tags, and the duplicate warning",
        ],
        "Editing or deleting cards, and bulk import (T14).",
    ),
    "T10": (
        "`review --tag <tag>`",
        "cli",
        ["T09", "T06"],
        "With tags in the file (T08), a way to create them (T09), and a bounded review "
        "session (T06), a learner can finally review one subject at a time.",
        [
            "`flashcards review --tag verb` reviews only due cards carrying that tag",
            "`--tag` and `--limit` compose: the tag filter applies first, then the limit",
            "The filter is a pure domain function, not a comprehension in `cli/main.py`",
            "An unknown tag reviews nothing and says which tags the deck does have",
            "Tests cover the composition with `--limit` and the unknown-tag message",
        ],
        "Multiple tags in one invocation, and boolean tag expressions.",
    ),
    "T11": (
        "Session stats aggregation",
        "domain",
        ["T02"],
        "Once review state persists (T02) the deck file contains a history worth "
        "summarising. This ticket computes the summary; it does not display it.",
        [
            "New module `src/flashcards/domain/stats.py`, pure, importing nothing from "
            "`storage/` or `cli/`",
            "Given a deck and `today`, returns total cards, cards due, cards never "
            "reviewed, mean ease factor, and mean interval",
            "An empty deck returns zeros rather than raising or dividing by zero",
            "Means exclude never-reviewed cards, and the docstring says so",
            "`tests/domain/test_stats.py` covers an empty deck, an all-new deck, and a "
            "mixed one",
        ],
        "Printing anything (T12) and grouping by tag (T13).",
    ),
    "T12": (
        "`stats` command",
        "cli",
        ["T11"],
        "T11 computes the numbers. This puts them on screen, in a form a person reading "
        "a terminal can take in at a glance.",
        [
            "`flashcards stats --deck <path>` prints every figure T11 returns, aligned "
            "and labelled",
            "Means print to one decimal place; an empty deck prints a one-line message "
            "instead of a table of zeros",
            "`cli/` does no arithmetic - it formats what `domain.stats` returned",
            "Tests assert the rendered text for a mixed deck and for an empty one",
        ],
        "Grouping by tag (T13) and any machine-readable output format.",
    ),
    "T13": (
        "`stats --by-tag`",
        "cli",
        ["T12", "T08"],
        "The most useful question a learner asks of their stats is which subject they "
        "are behind on. Answering it needs both the stats command (T12) and tags in the "
        "file (T08) - note that its two parents sit six tickets apart, in different "
        "layers.",
        [
            "`flashcards stats --by-tag` prints one row per tag, plus a row for untagged "
            "cards",
            "A card with two tags is counted under both, and the totals row says so "
            "rather than silently exceeding the deck size",
            "Rows are sorted by cards due, descending, then by tag name",
            "The grouping happens in `domain.stats`, not in `cli/`",
            "Tests cover a multi-tag card, untagged cards, and the sort order",
        ],
        "Filtering stats to a single tag, and any time-series view.",
    ),
    "T14": (
        "CSV import, including a tags column",
        "storage",
        ["T08"],
        "Nobody types a deck in one card at a time. Importing from a spreadsheet export "
        "is how a real deck gets started, and the tags column has to survive the trip.",
        [
            "New module `src/flashcards/storage/csv_io.py`",
            "`flashcards import --deck <path> --from <csv>` appends cards from a CSV "
            "with `front`, `back`, and optional `tags` columns",
            "The tags cell is semicolon-separated, so a comma can appear inside a tag",
            "A missing required column, or a row with the wrong field count, is reported "
            "with its line number and imports nothing",
            "Imported cards are appended, never overwriting the existing deck",
            "`tests/storage/test_csv_io.py` covers a clean import, a tags column, and "
            "each error case",
        ],
        "Export (T15), and any format other than CSV.",
    ),
    "T15": (
        "`export --format json|csv`",
        "cli",
        ["T14"],
        "The other half of T14. A deck a learner cannot get back out of the tool is a "
        "deck held hostage, and the CSV reader written in T14 gives the writer its shape "
        "to match.",
        [
            "`flashcards export --deck <path> --format json|csv [--out <path>]` writes "
            "the deck, defaulting to stdout",
            "CSV export round-trips through T14's importer with no loss of front, back, "
            "or tags",
            "JSON export is byte-identical to the deck file `save_deck` writes",
            "An unrecognised `--format` is a usage error listing the formats that exist",
            "Tests assert the CSV round trip and the JSON byte-identity",
        ],
        "Exporting review state to CSV - the round-trip guarantee covers content only.",
    ),
}


def waves() -> list[list[str]]:
    """Kahn's algorithm, level by level. Raises if the graph is not a DAG."""
    remaining = {tid: set(t[2]) for tid, t in TICKETS.items()}
    for tid, deps in remaining.items():
        unknown = deps - TICKETS.keys()
        if unknown:
            raise ValueError(f"{tid} blocked by unknown ticket(s): {sorted(unknown)}")
    out: list[list[str]] = []
    done: set[str] = set()
    while remaining:
        ready = sorted(t for t, deps in remaining.items() if deps <= done)
        if not ready:
            raise ValueError(f"cycle among {sorted(remaining)}")
        out.append(ready)
        done |= set(ready)
        for t in ready:
            del remaining[t]
    return out


def joins() -> list[str]:
    """Tickets with more than one blocking parent."""
    return sorted(t for t, v in TICKETS.items() if len(v[2]) > 1)


def body(tid: str, numbers: dict[str, int] | None = None) -> str:
    """Render one ticket's issue body. `numbers` maps ticket ids to issue numbers."""
    title, layer, blocked, context, acceptance, oos = TICKETS[tid]

    def ref(dep: str) -> str:
        if numbers and dep in numbers:
            return f"#{numbers[dep]}"
        return dep

    lines = [
        "## Context",
        "",
        context,
        "",
        "## Acceptance criteria",
        "",
        *[f"- [ ] {a}" for a in acceptance],
        "",
        "## Out of scope",
        "",
        oos,
        "",
        "## Blocked by",
        "",
    ]
    if blocked:
        for dep in blocked:
            lines.append(f"- {ref(dep)} - {TICKETS[dep][0]}")
        lines += [
            "",
            "Recorded as a GitHub issue dependency as well as in this list, so `gh` and "
            "the issue sidebar both show it.",
        ]
    else:
        lines.append("Nothing. This ticket can start today.")
    lines += ["", f"_Layer: `{layer}`_"]
    return "\n".join(lines)


if __name__ == "__main__":
    w = waves()
    print(f"tickets: {len(TICKETS)}")
    print("graph:   DAG (no cycle found)")
    for i, wave in enumerate(w, 1):
        print(f"  wave {i}  " + "  ".join(wave))
    print(f"depth:               {len(w)}")
    print(f"max parallel width:  {max(len(x) for x in w)}")
    print(f"two-parent joins:    {', '.join(joins())}")
