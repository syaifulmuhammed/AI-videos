// Shared helpers for the reel's scenes. Loaded once by index.html.
// Everything here only adds tweens or sets to a paused timeline, so any
// frame is a pure function of timeline time.
(function () {
  "use strict";

  var MINUS = "−";

  function format(value, decimals, signed) {
    var text = Math.abs(value).toFixed(decimals);
    if (Number(text) === 0) return text;
    if (value < 0) return MINUS + text;
    return signed ? "\u2060+" + text : text;
  }

  // Count `el` from `from` to `to`, one authored set per frame (the registry
  // count-up technique), so seeking backwards shows the same digits.
  function count(tl, el, opts) {
    var fps = 30;
    var frames = Math.max(1, Math.round(opts.duration * fps));
    var ease = gsap.parseEase(opts.ease || "sine.inOut");
    for (var f = 0; f <= frames; f += 1) {
      var v = opts.from + (opts.to - opts.from) * ease(f / frames);
      tl.set(el, { textContent: format(v, opts.decimals || 0, opts.signed) + (opts.suffix || "") }, opts.at + opts.duration * (f / frames));
    }
  }

  // Per-word blur-in: 0.13 s each, 0.067 s apart, no translate.
  function wordsIn(tl, words, at) {
    words.forEach(function (w, i) {
      tl.fromTo(w, { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power2.out" }, at + i * 0.067);
    });
  }

  // Per-word grey to ink, no position change.
  function wordsInk(tl, words, at, from, to) {
    words.forEach(function (w, i) {
      tl.fromTo(w, { color: from }, { color: to, duration: 0.18, ease: "power2.out" }, at + i * 0.085);
    });
  }

  // Wrap each word of an element's text in a span and return the spans.
  function splitWords(el) {
    var words = el.textContent.trim().split(/\s+/);
    el.textContent = "";
    return words.map(function (word, i) {
      var span = document.createElement("span");
      span.className = "w";
      span.textContent = word;
      el.appendChild(span);
      if (i < words.length - 1) el.appendChild(document.createTextNode(" "));
      return span;
    });
  }

  window.reel = { format: format, count: count, wordsIn: wordsIn, wordsInk: wordsInk, splitWords: splitWords };
})();
