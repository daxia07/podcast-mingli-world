// Asset-version consistency.
//
// AGENTS.md gotcha #6: the `?v=` query on the stylesheet and scripts in
// index.html and the `CACHE_V` in sw.js must be bumped together. Miss one and
// users get a new HTML shell with stale JS, or a service worker that caches
// URLs the page never requests. This turns that convention into a test.

import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const html = await readFile(join(root, 'site', 'index.html'), 'utf8');
const sw = await readFile(join(root, 'site', 'sw.js'), 'utf8');

const htmlVersions = [...html.matchAll(/(?:href|src)="\/[^"]*\?v=(\d+)"/g)].map((m) => m[1]);
const swVersion = /CACHE_V\s*=\s*"podcast-app-v(\d+)/.exec(sw)?.[1];

test('index.html references at least one versioned asset', () => {
  assert.ok(htmlVersions.length >= 4, `found ${htmlVersions.length} versioned assets`);
});

test('every versioned asset in index.html uses the same version', () => {
  const unique = [...new Set(htmlVersions)];
  assert.equal(unique.length, 1, `mixed asset versions in index.html: ${unique.join(', ')}`);
});

test('sw.js CACHE_V matches the asset version', () => {
  assert.ok(swVersion, 'could not parse CACHE_V from sw.js');
  assert.equal(swVersion, htmlVersions[0], 'bump CACHE_V and ?v= together');
});

test('every versioned script in index.html is precached by the worker', () => {
  const scripts = [...html.matchAll(/src="(\/[^"]*\.js\?v=\d+)"/g)].map((m) => m[1]);
  for (const src of scripts) {
    assert.ok(sw.includes(src), `sw.js SHELL is missing ${src}`);
  }
});

test('every shell entry the worker precaches is actually referenced', () => {
  const shell = [...sw.matchAll(/"(\/[^"]*\?v=\d+)"/g)].map((m) => m[1]);
  for (const entry of shell) {
    assert.ok(html.includes(entry), `sw.js precaches ${entry}, which index.html never loads`);
  }
});

test('scripts load in dependency order', () => {
  // player-ui.js calls window.VTT and window.Chapters at parse time, and reads
  // elements app.js also owns — it must come last.
  const order = [...html.matchAll(/src="\/(?:js\/)?([\w-]+)\.js/g)].map((m) => m[1]);
  assert.ok(order.indexOf('vtt') < order.indexOf('player-ui'), 'vtt.js must precede player-ui.js');
  assert.ok(order.indexOf('chapters') < order.indexOf('player-ui'), 'chapters.js must precede player-ui.js');
  assert.ok(order.indexOf('app') < order.indexOf('player-ui'), 'app.js must precede player-ui.js');
  // shelf.js defines window.Shelf, which shelf-ui.js reads at parse time and
  // app.js reads while rendering.
  assert.ok(order.indexOf('shelf') < order.indexOf('shelf-ui'), 'shelf.js must precede shelf-ui.js');
  assert.ok(order.indexOf('shelf') < order.indexOf('app'), 'shelf.js must precede app.js');
});
