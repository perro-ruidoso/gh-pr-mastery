/* Page behaviour for the course learning pages.

   Two jobs, both progressive enhancement — every page reads correctly
   with JavaScript off.

   1. Self-check questions, with a first-try tally per section. Markup contract:
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

   Flashcard decks are a separate component, flashcards.js, loaded only by
   pages that carry one.

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

  // Each .selfcheck keeps a first-try tally so the student gets one honest
  // number at the end, not just per-question colour.
  document.querySelectorAll(".selfcheck").forEach(function (sc) {
    var questions = sc.querySelectorAll(".q[data-answer]");
    if (!questions.length) return;
    var attempted = 0, firstTry = 0;
    var score = document.createElement("p");
    score.className = "sc-score";
    sc.appendChild(score);

    function renderScore() {
      if (!attempted) {
        score.textContent = questions.length + " questions. Your first click on each one is the one that counts.";
        return;
      }
      score.innerHTML = "First-try correct: <strong>" + firstTry + " / " + attempted + "</strong>" +
        (attempted < questions.length ? " (" + (questions.length - attempted) + " left)" :
          firstTry === questions.length ? " — all of them. Try the flashcards without looking back." :
          " — re-read the sections behind the ones you missed before moving on.");
    }
    renderScore();

    questions.forEach(function (q) {
      var answer = q.getAttribute("data-answer");
      var why = q.querySelector(".q-why");
      var touched = false;

      q.querySelectorAll(".q-opts button[data-opt]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var isCorrect = btn.getAttribute("data-opt") === answer;
          if (!touched) {
            touched = true;
            attempted += 1;
            if (isCorrect) firstTry += 1;
            renderScore();
          }
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
