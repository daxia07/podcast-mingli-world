---
name: show-new
description: Register a new show (playlist) end to end. Use when asked to add a new series, show, or playlist to the podcast.
---

# Add a new show

A show is a playlist in the manifest plus its presentation metadata. Both come
from one file — `content/shows.json`. `app.js` reads title, mono, description,
order and featured from the manifest at load time, so adding a show needs no
frontend edit. The `SHOW_META` and `SHOW_ORDER` constants still exist in
`app.js` but are only fallbacks for shows the manifest doesn't describe.

## 1. Register it

Add an entry to `content/shows.json`:

```jsonc
"infosec-interview": {
  "title": "Info Security Interview Prep",
  "description": "Security topics as interview answers.",
  "mono": "IS",                       // two letters, shown on the artwork tile
  "icon": "🔐",
  "default_template": "concept-explainer",
  "order": 12,                        // position in Home and Library
  "featured": false                   // large card on Home
}
```

Pick a `default_template` that already exists in `content/templates/`. If none
fits, create one first — copy the closest and rewrite its `sections` and
`authoring_brief`. A template is worth adding only when the format genuinely
differs; a variant of an existing show is not a new format.

## 2. Sync it into the manifest

```
python3 -c "
import json, pathlib, sys; sys.path.insert(0,'.')
from scripts.lib import manifest as M
m = M.load(); M.apply_shows(m, json.loads(pathlib.Path('content/shows.json').read_text())); M.save_local(m)"
python3 -m scripts.lib.gates --manifest
```

An empty show is a warning, not an error — but don't leave one sitting empty.
Two shows were registered with zero episodes for months and rendered as dead
tiles in the app.

## 3. Seed it

Write the first three episodes with the `episode-new` skill before shipping.
A show with one episode looks broken.

## 4. Verify

`npm run dev`, open the app, confirm the show appears on Home and Library with
its badge and description, and that its episodes play.
