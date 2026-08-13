// Tests for site/js/shelf.js — the shelving rules and the swipe thresholds.
//
// Loaded into a vm sandbox with a fake localStorage, the same way the browser
// sees it. The point of these is that the gesture maths and the visibility
// rules are the parts that are painful to debug by hand on a phone.

import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));

async function load() {
  const store = new Map();
  const sandbox = {
    window: {},
    localStorage: {
      getItem: (k) => (store.has(k) ? store.get(k) : null),
      setItem: (k, v) => store.set(k, String(v)),
      removeItem: (k) => store.delete(k),
    },
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  const src = await readFile(join(here, '..', 'site', 'js', 'shelf.js'), 'utf8');
  vm.runInContext(src, sandbox);
  return { Shelf: sandbox.window.Shelf, store };
}

// --- episode shelf --------------------------------------------------------

test('an episode starts unshelved and round-trips', async () => {
  const { Shelf } = await load();
  assert.equal(Shelf.isShelved(42), false);
  Shelf.setShelved(42, true);
  assert.equal(Shelf.isShelved(42), true);
  assert.equal(Shelf.shelvedCount(), 1);
  Shelf.setShelved(42, false);
  assert.equal(Shelf.isShelved(42), false);
  assert.equal(Shelf.shelvedCount(), 0);
});

test('numeric and string ids are the same episode', async () => {
  const { Shelf } = await load();
  Shelf.setShelved(7, true);
  assert.equal(Shelf.isShelved('7'), true);
});

test('corrupt storage degrades to empty rather than throwing', async () => {
  const { Shelf, store } = await load();
  store.set('pod_shelved', '{not json');
  assert.equal(Shelf.isShelved(1), false);
  assert.equal(Shelf.shelvedCount(), 0);
});

// --- visibility -----------------------------------------------------------

const PLAYLISTS = {
  'coding-prep': { id: 'coding-prep', archived: false },
  'airwallex-domain': { id: 'airwallex-domain', archived: true },
};

test('a normal episode in a live show is visible', async () => {
  const { Shelf } = await load();
  assert.equal(
    Shelf.episodeVisible({ id: 1, playlist: 'coding-prep' }, PLAYLISTS), true);
});

test('shelving hides an episode from a live show', async () => {
  const { Shelf } = await load();
  Shelf.setShelved(1, true);
  assert.equal(
    Shelf.episodeVisible({ id: 1, playlist: 'coding-prep' }, PLAYLISTS), false);
});

test('an episode of an archived show is hidden', async () => {
  const { Shelf } = await load();
  assert.equal(
    Shelf.episodeVisible({ id: 2, playlist: 'airwallex-domain', archived: true }, PLAYLISTS),
    false);
});

test('restoring the show brings its episodes back', async () => {
  const { Shelf } = await load();
  Shelf.setShowRestored('airwallex-domain', true);
  assert.equal(
    Shelf.episodeVisible({ id: 2, playlist: 'airwallex-domain', archived: true }, PLAYLISTS),
    true);
});

test('shelving still wins over a restored show', async () => {
  const { Shelf } = await load();
  Shelf.setShowRestored('airwallex-domain', true);
  Shelf.setShelved(2, true);
  assert.equal(
    Shelf.episodeVisible({ id: 2, playlist: 'airwallex-domain', archived: true }, PLAYLISTS),
    false);
});

test('showVisible follows the archived flag and the local override', async () => {
  const { Shelf } = await load();
  assert.equal(Shelf.showVisible(PLAYLISTS['coding-prep']), true);
  assert.equal(Shelf.showVisible(PLAYLISTS['airwallex-domain']), false);
  Shelf.setShowRestored('airwallex-domain', true);
  assert.equal(Shelf.showVisible(PLAYLISTS['airwallex-domain']), true);
});

// --- gesture --------------------------------------------------------------

test('a short drag springs back closed', async () => {
  const { Shelf } = await load();
  assert.equal(Shelf.swipeDecision(-20, 0, false), 'closed');
});

test('a medium drag opens the action', async () => {
  const { Shelf } = await load();
  assert.equal(Shelf.swipeDecision(-80, 0, false), 'open');
});

test('a long drag commits without needing the button', async () => {
  const { Shelf } = await load();
  assert.equal(Shelf.swipeDecision(-200, 0, false), 'commit');
});

test('a fast flick commits from a shorter drag', async () => {
  const { Shelf } = await load();
  assert.equal(Shelf.swipeDecision(-70, -1.5, false), 'commit');
  // ...but not if the drag never reached the reveal point.
  assert.equal(Shelf.swipeDecision(-30, -1.5, false), 'closed');
});

test('rightward movement never arms the action', async () => {
  const { Shelf } = await load();
  assert.equal(Shelf.swipeDecision(120, 2, false), 'closed');
});

test('an open row stays open unless pushed back right', async () => {
  const { Shelf } = await load();
  assert.equal(Shelf.swipeDecision(0, 0, true), 'open');
  assert.equal(Shelf.swipeDecision(40, 0, true), 'closed');
});

test('taps and vertical scrolls are not swipes', async () => {
  const { Shelf } = await load();
  assert.equal(Shelf.isHorizontalSwipe(3, 1), false);      // tap
  assert.equal(Shelf.isHorizontalSwipe(-15, 40), false);   // scrolling the list
  assert.equal(Shelf.isHorizontalSwipe(-40, 5), true);     // deliberate swipe
});

test('drag offset resists past the reveal point and never runs away', async () => {
  const { Shelf } = await load();
  assert.equal(Shelf.dragOffset(-30), -30);                  // 1:1 early
  assert.equal(Shelf.dragOffset(-Shelf.REVEAL_AT), -Shelf.REVEAL_AT);
  const far = Shelf.dragOffset(-400);
  assert.ok(far > -400, 'resistance applies');
  assert.ok(far < -Shelf.REVEAL_AT, 'still travels past the reveal point');
  // Rightward is rubber-banded to a small amount.
  assert.ok(Shelf.dragOffset(300) <= 24);
  assert.ok(Shelf.dragOffset(300) >= 0);
});
