// Theme tests — the palette discipline that dark mode failed on the first time.
//
// Dark mode was shipped once and pulled the same week: the palette flipped --ink
// to near-white while ~40 colours elsewhere in the stylesheet stayed hardcoded
// light, so cards drew white text on white. The fix was tokens; this file is
// what stops the tokens rotting.
//
// Three guards:
//   1. no raw colour anywhere outside the palette blocks
//   2. the light and dark palettes define exactly the same token names
//   3. the inline no-flash snippet in index.html agrees with js/theme.js

import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const css = await readFile(join(root, 'site', 'style.css'), 'utf8');
const html = await readFile(join(root, 'site', 'index.html'), 'utf8');

async function loadTheme() {
  const store = new Map();
  const sandbox = {
    window: {
      matchMedia: () => ({ matches: false, addEventListener() {}, addListener() {} }),
    },
    localStorage: {
      getItem: (k) => (store.has(k) ? store.get(k) : null),
      setItem: (k, v) => store.set(k, String(v)),
    },
    document: {
      readyState: 'complete',
      documentElement: { setAttribute() {}, removeAttribute() {} },
      querySelector: () => null,
      getElementById: () => null,
      addEventListener() {},
    },
    CustomEvent: class {
      constructor(type, init) { this.type = type; Object.assign(this, init); }
    },
  };
  sandbox.globalThis = sandbox;
  sandbox.window.dispatchEvent = () => {};
  vm.createContext(sandbox);
  vm.runInContext(await readFile(join(root, 'site', 'js', 'theme.js'), 'utf8'), sandbox);
  return sandbox.window.Theme;
}

/* The three blocks allowed to contain raw colour values. */
function paletteBlocks(source) {
  const blocks = [];
  const starts = [
    /^:root \{/m,
    /^@media \(prefers-color-scheme: dark\) \{/m,
    /^:root\[data-theme="dark"\] \{/m,
  ];
  for (const re of starts) {
    const m = re.exec(source);
    assert.ok(m, `missing palette block: ${re}`);
    // Walk braces from the match to find the end of the block.
    let depth = 0;
    let i = m.index;
    for (; i < source.length; i++) {
      if (source[i] === '{') depth++;
      else if (source[i] === '}' && --depth === 0) { i++; break; }
    }
    blocks.push([m.index, i]);
  }
  return blocks;
}

function tokensIn(block) {
  const found = new Map();
  const re = /(--[\w-]+)\s*:\s*([^;]+);/g;
  let m;
  while ((m = re.exec(block))) found.set(m[1], m[2].trim());
  return found;
}

const blocks = paletteBlocks(css);
const [lightBlock, mediaBlock, attrBlock] = blocks.map(([a, b]) => css.slice(a, b));

// --- 1. no raw colour outside the palette -----------------------------------

test('no raw colour value survives outside the palette blocks', () => {
  // Blank out the palettes, keeping offsets so the reported line number is real.
  let rest = css;
  for (const [a, b] of blocks) {
    rest = rest.slice(0, a) + rest.slice(a, b).replace(/[^\n]/g, ' ') + rest.slice(b);
  }
  const offenders = [];
  rest.split('\n').forEach((line, i) => {
    const code = line.replace(/\/\*.*?\*\//g, '');
    if (/#[0-9a-fA-F]{3,8}\b/.test(code) || /\brgba?\s*\(/.test(code)) {
      offenders.push(`style.css:${i + 1}: ${line.trim()}`);
    }
  });
  assert.deepEqual(
    offenders,
    [],
    `hardcoded colours must become tokens or dark mode breaks:\n${offenders.join('\n')}`
  );
});

test('the stylesheet still contains colours — the guard is not vacuous', () => {
  assert.ok(tokensIn(lightBlock).size > 30, 'the light palette should be substantial');
});

// --- 2. the palettes agree ---------------------------------------------------

test('both dark palettes define exactly the same tokens', () => {
  const media = [...tokensIn(mediaBlock).keys()].sort();
  const attr = [...tokensIn(attrBlock).keys()].sort();
  assert.deepEqual(attr, media, 'the media-query and data-theme palettes have drifted');
});

test('both dark palettes give every token the same value', () => {
  const media = tokensIn(mediaBlock);
  const attr = tokensIn(attrBlock);
  const differing = [...media.keys()].filter((k) => attr.get(k) !== media.get(k));
  assert.deepEqual(differing, [], 'same token, different value in the two dark blocks');
});

test('every token the dark palette overrides exists in the light one', () => {
  const light = tokensIn(lightBlock);
  const missing = [...tokensIn(mediaBlock).keys()].filter((k) => !light.has(k));
  assert.deepEqual(missing, [], 'dark defines tokens :root never declares');
});

test('every colour token has a dark counterpart', () => {
  // Sizes, fonts and easings are theme-independent; colours are not. A token
  // whose light value is a colour but which dark leaves alone is the exact
  // failure mode that broke this the first time.
  const dark = tokensIn(mediaBlock);
  const isColour = (v) => /#[0-9a-fA-F]{3,8}\b/.test(v) || /\brgba?\s*\(/.test(v);
  const uncovered = [...tokensIn(lightBlock)]
    .filter(([k, v]) => isColour(v) && !dark.has(k))
    .map(([k]) => k);
  assert.deepEqual(uncovered, [], 'these colours would stay light on a dark phone');
});

// --- 3. the no-flash snippet agrees with theme.js ----------------------------

test('theme.js resolves the three states correctly', async () => {
  const T = await loadTheme();
  assert.equal(T.effective('system', true), 'dark');
  assert.equal(T.effective('system', false), 'light');
  assert.equal(T.effective('dark', false), 'dark', 'an explicit choice beats the OS');
  assert.equal(T.effective('light', true), 'light');
  assert.equal(T.effective('nonsense', true), 'dark', 'junk in storage falls back to system');
});

test('only an explicit choice writes the attribute', async () => {
  const T = await loadTheme();
  assert.equal(T.attribute('system'), null);
  assert.equal(T.attribute('dark'), 'dark');
  assert.equal(T.attribute('light'), 'light');
});

test('the bar colours match the --bg of each palette', async () => {
  const T = await loadTheme();
  assert.equal(tokensIn(lightBlock).get('--bg'), T.BAR.light);
  assert.equal(tokensIn(mediaBlock).get('--bg'), T.BAR.dark);
});

test('the inline boot snippet uses the same key and colour as theme.js', async () => {
  const T = await loadTheme();
  const head = html.slice(0, html.indexOf('</head>'));
  assert.ok(head.includes(`localStorage.getItem("${T.KEY}")`), 'boot snippet reads pod_theme');
  assert.ok(head.includes(T.BAR.dark), 'boot snippet paints the dark --bg');
  assert.ok(
    head.indexOf('data-theme') < head.indexOf('style.css'),
    'the attribute must be set before the stylesheet loads, or dark phones flash white'
  );
});

test('the Appearance control offers exactly the three states', async () => {
  const T = await loadTheme();
  const choices = [...html.matchAll(/data-theme-choice="(\w+)"/g)].map((m) => m[1]);
  // T.CHOICES comes from the vm realm, so compare as a joined string rather
  // than deepEqual, which would fail on the foreign Array prototype.
  assert.equal(choices.join(','), [].join.call(T.CHOICES, ','));
});
