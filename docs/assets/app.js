/* Page behaviour for the course learning pages.

   Two jobs, both progressive enhancement — every page reads correctly
   with JavaScript off.

   1. Self-check questions. Markup contract:
        <div class="q" data-answer="b">
          <p class="q-text">…</p>
          <ol class="q-opts">
            <li><button data-opt="a">…</button></li>
          </ol>
          <div class="q-why" hidden>…</div>
        </div>
      Clicking an option marks it right/wrong; the rationale reveals once
      the correct option has been found. Options stay clickable so students
      can explore why the others are wrong.

   2. Mermaid diagrams. Markup contract:
        <figure class="diagram">
          <pre class="mermaid">graph LR; …</pre>
          <figcaption class="caption">…</figcaption>
        </figure>
      mermaid.min.js is vendored beside this file; see adr/0001.
*/
(function () {
  "use strict";

  /* ---------- self-check ---------- */

  document.querySelectorAll(".q[data-answer]").forEach(function (q) {
    var answer = q.getAttribute("data-answer");
    var why = q.querySelector(".q-why");

    q.querySelectorAll(".q-opts button[data-opt]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var isCorrect = btn.getAttribute("data-opt") === answer;
        btn.classList.remove("correct", "incorrect");
        btn.classList.add(isCorrect ? "correct" : "incorrect");
        if (isCorrect && why) {
          why.hidden = false;
          q.querySelectorAll("button.incorrect").forEach(function (other) {
            if (other !== btn) other.classList.remove("incorrect");
          });
        }
      });
    });
  });

  /* ---------- mermaid ---------- */

  if (window.mermaid && document.querySelector("pre.mermaid")) {
    var dark = window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;

    window.mermaid.initialize({
      startOnLoad: true,
      theme: dark ? "dark" : "neutral",
      securityLevel: "strict",
      gitGraph: { showBranches: true, showCommitLabel: true },
      themeVariables: dark
        ? { primaryColor: "#2b1f3d", primaryTextColor: "#e6e6e3", lineColor: "#9aa4af" }
        : { primaryColor: "#f2ecfd", primaryTextColor: "#1f2328", lineColor: "#57606a" }
    });
  }
})();
