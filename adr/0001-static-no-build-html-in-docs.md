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

Vendored JS is limited to two files: `mermaid.min.js` (diagram rendering) and
`widgets.js` (Self-Checks plus the single bespoke widget, the merge-strategy simulator).
Both are committed, pinned, and loaded with plain `<script>` tags.

This mirrors the decision already made for the `claude_10` course repo, deliberately, so
the two sites share conventions.
