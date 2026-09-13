# Static no-build HTML served from docs/

The course learning pages are hand-authored static HTML with one shared stylesheet and a
small amount of vendored vanilla JS — no TypeScript, no framework, no build step —
despite the repo owner's default convention of TypeScript for web builds. The pages are
content, not an application: students and graders must be able to open them from a
`file://` URL or any static host with zero tooling, and a toolchain would add maintenance
cost with no functional payoff.

The site lives in `docs/` so classic GitHub Pages can serve it from `main /docs` without
an Actions workflow. As a consequence, ADRs live in `adr/` at the repo root rather than
the conventional `docs/adr/`, which would be published with the site.

Vendored and hand-written JS is limited to a few small files, each loaded with a plain
`<script>` tag: `mermaid.min.js` (diagram rendering, vendored and pinned), `app.js`
(Self-Checks and Mermaid init), and `flashcards.js` (the flashcard deck component). The
merge-strategy simulator planned for Week 5 will be a fourth. Every component is progressive
enhancement: a page reads correctly, and prints, with JavaScript off.

Learning Pages are organised one folder per objective (`docs/week-NN/mNN-slug/`) with an
`index.html` entry page and supporting pages beside it, so a dense objective can be split
without the Week Hub or the objectives workbook needing to know how many pages it has.

This mirrors the decision already made for the `claude_10` course repo, deliberately, so
the two sites share conventions.
