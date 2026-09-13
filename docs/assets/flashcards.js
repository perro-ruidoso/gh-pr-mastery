/* Flashcard decks for the course learning pages.

   Progressive enhancement: without JavaScript (or in print) a deck is a plain
   question/answer list. With it, the list is replaced by a one-card-at-a-time
   stage that runs a small Leitner loop — "Again" sends the card to the back of
   the queue, "Got it" retires it — so the student has to retrieve each answer
   before seeing it, which is what builds long-term retention.

   Markup contract:
     <section class="flashcards" data-deck="w1-m02-index">
       <h2>Flashcards</h2>
       <p class="fc-hint">…</p>
       <div class="fc-deck">
         <div class="fc">
           <div class="fc-front">Question</div>
           <div class="fc-back">Answer</div>
         </div>
       </div>
     </section>

   Keyboard, once a deck has focus: Space/Enter flips, 1 = Again, 2 = Got it.
   The only thing persisted (localStorage, best effort) is when the deck was
   last studied and how many cards needed a second look — enough to nudge a
   spaced review, never the answers themselves.
*/
(function () {
  "use strict";

  var STORE_PREFIX = "gh-pr-mastery:fc:";

  function load(key) {
    try { return JSON.parse(window.localStorage.getItem(STORE_PREFIX + key)) || null; }
    catch (e) { return null; }
  }

  function save(key, value) {
    try { window.localStorage.setItem(STORE_PREFIX + key, JSON.stringify(value)); }
    catch (e) { /* private window, blocked storage — fine */ }
  }

  function daysAgo(iso) {
    var ms = Date.now() - new Date(iso).getTime();
    var d = Math.floor(ms / 86400000);
    if (d <= 0) return "today";
    if (d === 1) return "yesterday";
    return d + " days ago";
  }

  function shuffle(arr) {
    for (var i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }
    return arr;
  }

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  function buildDeck(section) {
    var list = section.querySelector(".fc-deck");
    if (!list) return;
    var cards = Array.prototype.map.call(list.querySelectorAll(".fc"), function (fc) {
      var f = fc.querySelector(".fc-front"), b = fc.querySelector(".fc-back");
      return { front: f ? f.innerHTML : "", back: b ? b.innerHTML : "" };
    });
    if (!cards.length) return;

    var deckId = section.getAttribute("data-deck") || location.pathname;
    var stage = el("div", "fc-stage");
    var card = el("div", "fc-card");
    card.setAttribute("tabindex", "0");
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", "Flashcard. Activate to flip.");
    var sideLabel = el("span", "side-label");
    var text = el("div", "fc-text");
    card.appendChild(sideLabel);
    card.appendChild(text);

    var controls = el("div", "fc-controls");
    var flipBtn = el("button", "flip", "Flip");
    var againBtn = el("button", "again", "Again <span class=\"dim\">(1)</span>");
    var gotBtn = el("button", "got", "Got it <span class=\"dim\">(2)</span>");
    var progress = el("span", "fc-progress");
    controls.appendChild(flipBtn);
    controls.appendChild(againBtn);
    controls.appendChild(gotBtn);
    controls.appendChild(progress);

    var done = el("div", "fc-done");
    done.hidden = true;

    var meta = el("div", "fc-meta");

    stage.appendChild(card);
    stage.appendChild(controls);
    stage.appendChild(done);
    list.hidden = true;
    list.insertAdjacentElement("afterend", stage);
    stage.insertAdjacentElement("afterend", meta);

    var queue, retired, lapses, flipped, current;

    function start() {
      queue = shuffle(cards.slice());
      retired = 0;
      lapses = 0;
      done.hidden = true;
      card.hidden = false;
      controls.hidden = false;
      next();
    }

    function next() {
      if (!queue.length) return finish();
      current = queue[0];
      flipped = false;
      render();
    }

    function render() {
      card.classList.toggle("flipped", flipped);
      sideLabel.textContent = flipped ? "Answer" : "Question — say it, then flip";
      text.innerHTML = flipped ? current.back : current.front;
      againBtn.disabled = !flipped;
      gotBtn.disabled = !flipped;
      flipBtn.textContent = flipped ? "Show question" : "Flip";
      progress.textContent = queue.length + " to go · " + retired + " done";
    }

    function flip() { flipped = !flipped; render(); }

    function again() {
      if (!flipped) return;
      lapses += 1;
      queue.push(queue.shift());
      next();
    }

    function got() {
      if (!flipped) return;
      queue.shift();
      retired += 1;
      next();
    }

    function finish() {
      card.hidden = true;
      controls.hidden = true;
      done.hidden = false;
      var verdict = lapses === 0
        ? "Every card on the first pass. Come back in a few days and see if that holds — that is the test that matters."
        : lapses + (lapses === 1 ? " card needed" : " cards needed") + " a second look. Re-read the matching section, then run the deck again tomorrow rather than now.";
      done.innerHTML = "<p><strong>Deck complete — " + cards.length + " cards.</strong></p><p>" + verdict + "</p>";
      var againAll = el("button", "", "Study again");
      againAll.addEventListener("click", start);
      done.appendChild(againAll);
      save(deckId, { lastStudied: new Date().toISOString(), lapses: lapses, cards: cards.length });
      renderMeta();
    }

    function renderMeta() {
      var prior = load(deckId);
      meta.innerHTML = "";
      var bits = [];
      if (prior && prior.lastStudied) {
        bits.push("Last studied " + daysAgo(prior.lastStudied) +
          (prior.lapses ? " · " + prior.lapses + " needed a second look" : " · clean pass"));
      }
      var showList = el("button", "", "Show all cards as a list");
      showList.addEventListener("click", function () {
        list.hidden = !list.hidden;
        showList.textContent = list.hidden ? "Show all cards as a list" : "Hide the list";
      });
      if (bits.length) meta.appendChild(document.createTextNode(bits.join(" · ") + " · "));
      meta.appendChild(showList);
    }

    card.addEventListener("click", flip);
    flipBtn.addEventListener("click", flip);
    againBtn.addEventListener("click", again);
    gotBtn.addEventListener("click", got);
    section.addEventListener("keydown", function (ev) {
      if (ev.target.tagName === "BUTTON" && ev.key !== "1" && ev.key !== "2") return;
      if (ev.key === " " || ev.key === "Enter") { ev.preventDefault(); flip(); }
      else if (ev.key === "1") { ev.preventDefault(); again(); }
      else if (ev.key === "2") { ev.preventDefault(); got(); }
    });

    renderMeta();
    start();
  }

  document.querySelectorAll(".flashcards").forEach(buildDeck);
})();
