/*
 * searchable-select.js — turn a long <select> into a type-to-filter picker.
 *
 * Why hand-rolled instead of select2 / Tom Select / Choices.js:
 * this is a packaged OFFLINE desktop application. A CDN-hosted widget cannot
 * load on a clinic machine with no internet, and vendoring a third-party
 * bundle would mean shipping and maintaining code we did not write. The
 * drug picker holds ~1,555 options, which is the only list on the form long
 * enough to be genuinely painful to scroll — so a small vanilla enhancer is
 * the whole requirement.
 *
 * The critical design constraint: the prescription form's existing JavaScript
 * drives these selects directly. It sets `select.value` by hand, rebuilds the
 * option list with `sel.innerHTML = ''`, and reads `sel.options[...]` to build
 * the duplicate-class warning. So this script must NOT replace or wrap the
 * native <select> in a way that breaks any of that. Instead it:
 *
 *   1. hides the native <select> (a hidden select still POSTs),
 *   2. renders a text box + filtered list beside it,
 *   3. writes the choice back to the real select and dispatches a real
 *      bubbling `change` event, which is exactly what the existing
 *      `sel.addEventListener('change', ...)` handlers are already listening for.
 *
 * Everything that mutates the underlying select from outside — `fill()`,
 * `pick()`, the drug `change` handler — is picked up by a MutationObserver,
 * plus an explicit refresh on focus, so the visible label can never drift out
 * of sync with the real selection.
 */
(function () {
  'use strict';

  // Guard against enhancing the same <select> twice (e.g. if this script is
  // included on a page that re-initialises, or by an HTMX swap).
  var ENHANCED = 'ssEnhanced';

  // Cap rendered rows. Typing "a" matches most of the formulary; drawing 1,500
  // <li> nodes on every keystroke is what makes naive comboboxes jank.
  var MAX_ROWS = 120;

  // Fold accents and punctuation so "cotrimoxazole" finds "Cotrimoxazole",
  // "amoxi" finds "Amoxicillin", and "co amox" finds "Co-amoxiclav".
  function norm(s) {
    var t = String(s == null ? '' : s);
    if (t.normalize) t = t.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    return t.toLowerCase().replace(/[^a-z0-9+]+/g, ' ').trim();
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  /* ---------------------------------------------------------------- build */

  function build(sel) {
    var wrap = el('div', 'ss');
    var box = el('div', 'ss-box');
    var input = el('input', 'ss-input');
    var caret = el('button', 'ss-caret');
    caret.type = 'button';
    caret.tabIndex = -1;
    caret.setAttribute('aria-hidden', 'true');
    caret.innerHTML = '&#9662;';   // small down triangle

    input.type = 'text';
    input.setAttribute('autocomplete', 'off');
    input.setAttribute('spellcheck', 'false');
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-expanded', 'false');
    input.setAttribute('aria-autocomplete', 'list');
    // A hidden select is still submitted, so the form contract is unchanged.
    sel.classList.add('ss-native');
    sel.setAttribute('aria-hidden', 'true');
    // Keep the option text reachable to screen readers via the native select.
    sel.tabIndex = -1;

    box.appendChild(input);
    box.appendChild(caret);

    var list = el('ul', 'ss-list');
    list.setAttribute('role', 'listbox');
    list.hidden = true;

    wrap.appendChild(box);
    wrap.appendChild(list);
    sel.parentNode.insertBefore(wrap, sel.nextSibling);

    return { sel: sel, wrap: wrap, box: box, input: input, list: list, caret: caret,
             rows: [], active: -1, open: false };
  }

  /* --------------------------------------------------------- option cache */

  // Read the live <select> into a flat array of entries, remembering each
  // option's <optgroup> so headings can be reproduced.
  function readOptions(sel) {
    var out = [];
    for (var i = 0; i < sel.options.length; i++) {
      var o = sel.options[i];
      var parent = o.parentNode;
      out.push({
        opt: o,
        value: o.value,
        label: (o.textContent || '').trim(),
        // data-search lets a view supply a wider match key than the visible
        // label — the drug picker uses it for brand names and strengths.
        search: o.getAttribute('data-search') || (o.textContent || ''),
        group: (parent && parent.tagName === 'OPTGROUP')
                 ? (parent.label || '') : ''
      });
    }
    return out;
  }

  function labelFor(entries, value) {
    for (var i = 0; i < entries.length; i++) {
      if (entries[i].value === value) return entries[i].label;
    }
    return '';
  }

  /* ------------------------------------------------------------- filtering */

  // Every whitespace-separated token must appear somewhere in the entry, so
  // "pred 20" narrows rather than widening. Prefix-matching is not required:
  // a prescriber typing "nis" should find Nystatin, not only Nifedipine.
  function matches(entry, tokens) {
    var hay = entry._n;
    for (var i = 0; i < tokens.length; i++) {
      if (hay.indexOf(tokens[i]) === -1) return false;
    }
    return true;
  }

  /* --------------------------------------------------------------- render */

  function render(st, filterText) {
    var tokens = norm(filterText).split(' ').filter(Boolean);
    var entries = st.rows;
    var hits = [];
    var truncated = 0;

    for (var i = 0; i < entries.length; i++) {
      var e = entries[i];
      e._n = norm(e.search + ' ' + e.label + ' ' + e.group);
      if (tokens.length && !matches(e, tokens)) continue;
      if (hits.length < MAX_ROWS) hits.push(e); else truncated++;
    }

    st.list.innerHTML = '';
    st.active = hits.length ? 0 : -1;

    var lastGroup = null;
    for (var j = 0; j < hits.length; j++) {
      var h = hits[j];
      if (h.group && h.group !== lastGroup) {
        lastGroup = h.group;
        var gh = el('li', 'ss-group', h.group);
        gh.setAttribute('role', 'presentation');
        st.list.appendChild(gh);
      }
      var li = el('li', 'ss-opt', h.label);
      li.setAttribute('role', 'option');
      li.setAttribute('data-i', String(j));
      if (h.opt.selected) li.classList.add('is-sel');
      if (j === st.active) li.classList.add('is-active');
      // A brand/strength hit that is not in the visible label: show why it
      // matched, otherwise "it found my drug but I cannot see why" is worse
      // than no search at all.
      if (tokens.length && norm(h.label).indexOf(tokens.join(' ')) === -1) {
        var why = extraMatch(h, tokens);
        if (why) {
          var em = el('span', 'ss-why', why);
          li.appendChild(em);
        }
      }
      st.list.appendChild(li);
    }

    if (hits.length) {
      st.hits = hits;
    } else {
      st.hits = [];
      var none = el('li', 'ss-none', 'No match');
      none.setAttribute('role', 'presentation');
      st.list.appendChild(none);
    }

    if (truncated) {
      var more = el('li', 'ss-more',
        (truncated) + ' more match' + (truncated === 1 ? '' : 'es') +
        ' — keep typing to narrow');
      more.setAttribute('role', 'presentation');
      st.list.appendChild(more);
    }
  }

  // Return the matched fragment of the hidden search key (brand, strength) so
  // the prescriber can tell two same-generic rows apart.
  function extraMatch(entry, tokens) {
    var src = norm(entry.search);
    for (var i = 0; i < tokens.length; i++) {
      var at = src.indexOf(tokens[i]);
      if (at !== -1) {
        var from = Math.max(0, at - 12);
        return (from ? '…' : '') + entry.search.slice(from, at + tokens[i].length + 18) + '…';
      }
    }
    return '';
  }

  /* ----------------------------------------------------------------- open */

  function openList(st) {
    st.open = true;
    st.list.hidden = false;
    st.input.setAttribute('aria-expanded', 'true');
    // Show the current label in the box, and filter from empty text.
    st.input.value = '';
    st.filter = '';
    render(st, '');
    st.input.focus();
  }

  function closeList(st, keepLabel) {
    st.open = false;
    st.list.hidden = true;
    st.input.setAttribute('aria-expanded', 'false');
    st.input.value = keepLabel === false ? '' : currentLabel(st);
    st.input.classList.remove('is-typing');
  }

  function currentLabel(st) {
    var sel = st.sel;
    if (sel.selectedIndex < 0) return '';
    return (sel.options[sel.selectedIndex].textContent || '').trim();
  }

  // Public: re-read the native select and re-label the box. Called by the
  // MutationObserver and on focus, because the form's own code mutates these
  // selects directly (`sel.value = x`, `sel.innerHTML = ''`).
  function refresh(sel) {
    var st = sel[ENHANCED];
    if (!st) return;
    st.rows = readOptions(sel);
    if (!st.open) {
      st.input.value = currentLabel(st);
    } else {
      render(st, st.input.value);
    }
  }

  /* -------------------------------------------------------------- commit */

  function commit(st, entry) {
    if (!entry) return;
    st.sel.value = entry.value;
    closeList(st);
    // The form's auto-fill, dependent selects and duplicate-class warning all
    // hang off `change`; firing a real one keeps them working untouched.
    st.sel.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function setActive(st, i) {
    var items = st.list.querySelectorAll('.ss-opt');
    if (!items.length) return;
    st.active = Math.max(0, Math.min(i, items.length - 1));
    for (var k = 0; k < items.length; k++) {
      items[k].classList.toggle('is-active', k === st.active);
    }
    var node = items[st.active];
    if (node.scrollIntoView) node.scrollIntoView({ block: 'nearest' });
  }

  /* ------------------------------------------------------------- enhance */

  function enhance(sel) {
    if (!sel || sel[ENHANCED] || sel.dataset.ssSkip === '1') return null;

    var st = build(sel);
    st[ENHANCED] = st;
    sel[ENHANCED] = st;
    st.rows = readOptions(sel);
    st.input.value = currentLabel(st);

    st.input.addEventListener('focus', function () {
      refresh(sel);
      if (!st.open) openList(st);
    });

    st.input.addEventListener('input', function () {
      st.filter = st.input.value;
      if (!st.open) { st.open = true; st.list.hidden = false;
                      st.input.setAttribute('aria-expanded', 'true'); }
      render(st, st.filter);
    });

    st.caret.addEventListener('mousedown', function (e) {
      e.preventDefault();
      if (st.open) closeList(st); else openList(st);
    });

    // populateRow / remove-row set sel.value without mutating options.
    st.sel.addEventListener('change', function () {
      if (!st.open) st.input.value = currentLabel(st);
    });

    st.list.addEventListener('mousedown', function (e) {
      var li = e.target.closest('.ss-opt');
      if (!li) return;
      e.preventDefault();               // don't blur before the click lands
      commit(st, st.hits[+li.getAttribute('data-i')]);
    });

    st.list.addEventListener('mousemove', function (e) {
      var li = e.target.closest('.ss-opt');
      if (li) setActive(st, +li.getAttribute('data-i'));
    });

    st.input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!st.open) { openList(st); return; }
        setActive(st, st.active + (e.key === 'ArrowDown' ? 1 : -1));
      } else if (e.key === 'Enter') {
        // Enter must not submit the prescription form while picking a value.
        e.preventDefault();
        if (st.open) commit(st, st.hits[st.active]);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        closeList(st);
      } else if (e.key === 'Tab') {
        closeList(st);
      }
    });

    // Any external mutation of the select (the form rebuilds brand / strength
    // / frequency option lists on every drug or route change) is picked up
    // here, so the visible label and the cached options never go stale.
    if (window.MutationObserver) {
      new MutationObserver(function () { refresh(sel); })
        .observe(sel, { childList: true, subtree: true });
    }

    st.wrap.addEventListener('focusout', function (e) {
      if (st.wrap.contains(e.relatedTarget)) return;
      closeList(st);
    });

    return st;
  }

  function enhanceAll(root, selector) {
    var scope = root || document;
    var found = scope.querySelectorAll(selector || 'select');
    for (var i = 0; i < found.length; i++) enhance(found[i]);
    return found.length;
  }

  window.SearchableSelect = {
    enhance: enhance,
    enhanceAll: enhanceAll,
    refresh: function (sel) { refresh(sel); },
    norm: norm
  };

  // Opt-in only — long lists (prescription drug picker) pass an explicit selector.
  var AUTO = 'select.drug-select';

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      if (document.querySelector(AUTO)) enhanceAll(document, AUTO);
    });
  } else if (document.querySelector(AUTO)) {
    enhanceAll(document, AUTO);
  }
})();
