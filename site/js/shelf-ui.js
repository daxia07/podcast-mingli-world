/* shelf-ui.js — the swipe gesture and its affordances.
 *
 * Wraps each episode row in a container with an action sitting behind it, then
 * drags the row to reveal it. Pointer events, transforms, no library.
 *
 * Three behaviours worth calling out, because they are what makes a swipe row
 * feel right rather than fighting you:
 *
 *  - A drag that is mostly vertical is handed back to the list so scrolling
 *    still works; the row only takes over once the movement is clearly sideways.
 *  - A swipe suppresses the click that would otherwise fire on release, so you
 *    never shelve an episode and start playing it in the same gesture.
 *  - Every commit is undoable from the toast. Shelving is reversible, but only
 *    if you can find the Shelved tab — an Undo means you do not have to.
 *
 * Depends on window.Shelf (shelf.js) for the thresholds and the state.
 */
(function () {
  'use strict';

  var Shelf = window.Shelf;
  if (!Shelf) return;

  var openRow = null;
  var drag = null;

  function closeOpenRow() {
    if (!openRow) return;
    openRow.classList.remove('open');
    var card = openRow.querySelector('.ep-card');
    if (card) card.style.transform = '';
    openRow = null;
  }

  function rowFrom(target) {
    return target.closest ? target.closest('.ep-swipe') : null;
  }

  // ——— gesture ———

  document.addEventListener(
    'pointerdown',
    function (e) {
      var row = rowFrom(e.target);
      if (!row) {
        closeOpenRow();
        return;
      }
      // Let the action button handle its own taps.
      if (e.target.closest('.ep-action')) return;

      drag = {
        row: row,
        card: row.querySelector('.ep-card'),
        startX: e.clientX,
        startY: e.clientY,
        startedAt: Date.now(),
        wasOpen: row.classList.contains('open'),
        active: false,
        moved: false
      };
    },
    { passive: true }
  );

  document.addEventListener(
    'pointermove',
    function (e) {
      if (!drag || !drag.card) return;
      var dx = e.clientX - drag.startX;
      var dy = e.clientY - drag.startY;

      if (!drag.active) {
        // Undecided: only claim the gesture once it is clearly horizontal,
        // otherwise the list must stay scrollable.
        if (!Shelf.isHorizontalSwipe(dx, dy)) return;
        drag.active = true;
        drag.row.classList.add('dragging');
      }

      drag.moved = true;
      var base = drag.wasOpen ? -Shelf.REVEAL_AT : 0;
      drag.card.style.transform = 'translateX(' + (base + Shelf.dragOffset(dx)) + 'px)';
    },
    { passive: true }
  );

  function endDrag(e) {
    if (!drag) return;
    var d = drag;
    drag = null;
    if (!d.card) return;

    d.row.classList.remove('dragging');
    if (!d.active) return;

    var dx = (e.clientX || d.startX) - d.startX;
    var elapsed = Math.max(1, Date.now() - d.startedAt);
    var decision = Shelf.swipeDecision(dx, dx / elapsed, d.wasOpen);

    // Swallow the click this release would otherwise produce.
    if (d.moved) {
      d.row.dataset.suppressClick = '1';
      setTimeout(function () { delete d.row.dataset.suppressClick; }, 350);
    }

    if (decision === 'commit') {
      d.card.style.transform = '';
      commit(d.row);
      return;
    }
    if (decision === 'open') {
      closeOpenRow();
      d.row.classList.add('open');
      d.card.style.transform = 'translateX(' + -Shelf.REVEAL_AT + 'px)';
      openRow = d.row;
      return;
    }
    d.row.classList.remove('open');
    d.card.style.transform = '';
    if (openRow === d.row) openRow = null;
  }

  document.addEventListener('pointerup', endDrag);
  document.addEventListener('pointercancel', endDrag);

  // ——— committing ———

  function commit(row) {
    var id = row.dataset.id;
    var showId = row.dataset.show;
    var wasShelved = row.dataset.shelved === '1';

    if (showId) {
      // A show row in the Shelved tab: restore the whole show.
      Shelf.setShowRestored(showId, true);
      announce('Show restored', function () {
        Shelf.setShowRestored(showId, false);
      });
    } else {
      Shelf.setShelved(id, !wasShelved);
      announce(wasShelved ? 'Unshelved' : 'Shelved', function () {
        Shelf.setShelved(id, wasShelved);
      });
    }

    closeOpenRow();
    window.dispatchEvent(new CustomEvent('shelf:change'));
  }

  document.addEventListener('click', function (e) {
    var action = e.target.closest('.ep-action');
    if (action) {
      e.preventDefault();
      e.stopPropagation();
      commit(action.closest('.ep-swipe'));
      return;
    }
    // Kill the click that ends a swipe, in the capture-ish sense: the row's own
    // handler runs on .ep-card, so checking the wrapper here is enough.
    var row = rowFrom(e.target);
    if (row && row.dataset.suppressClick) {
      e.preventDefault();
      e.stopPropagation();
    }
  }, true);

  // ——— undo toast ———

  var undoTimer = 0;

  function announce(message, undo) {
    var toast = document.getElementById('shelfToast');
    if (!toast) return;
    toast.innerHTML =
      '<span>' + message + '</span><button type="button" id="shelfUndo">Undo</button>';
    toast.classList.add('on');

    clearTimeout(undoTimer);
    undoTimer = setTimeout(function () { toast.classList.remove('on'); }, 5000);

    document.getElementById('shelfUndo').onclick = function () {
      undo();
      toast.classList.remove('on');
      window.dispatchEvent(new CustomEvent('shelf:change'));
    };
  }

  // Scrolling anywhere dismisses an open row — matches every native list.
  document.addEventListener('scroll', closeOpenRow, true);
})();
