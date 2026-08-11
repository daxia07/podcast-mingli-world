---
name: episode-new
description: Author a new podcast episode as a blueprint and build it. Use when asked to create, write, or add an episode to any show on podcast.mingli.world.
---

# Create a new episode

The only supported way to add an episode. Do **not** write a new `generate_*.py`
script — those are frozen legacy. Content is data: one blueprint JSON in, one
command out.

## 1. Pick the show and template

Read `content/shows.json`. Each show declares a `default_template`. Read that
template from `content/templates/<name>.json` — it holds the section plan, the
target duration range, and an `authoring_brief` per section that says what
belongs there and what to avoid.

If the user hasn't said which show, ask. Don't guess: the show determines the
voices, the format, and where it appears in the app.

## 2. Interview the user — at most three questions

You need the topic, the angle, and anything specific they want covered. Batch
the questions into one message. If the request already contains all three,
skip this step and say what you inferred.

## 3. Write the blueprint

Create `content/blueprints/<show>/<slug>.json`. Shape is in
`docs/UPGRADE-SPEC.md` §4.1; copy a neighbour in the same folder for reference.

Rules that the gates enforce, so save yourself a round trip:

- **Spoken text only.** No markdown, no backticks, no bullet characters, no
  URLs, no ampersands, no `O(n^2)` — write "O of n squared". Say numbers in
  words where a reader would stumble.
- **One line per spoken beat**, not per paragraph. Lines are the transcript
  cues and the unit of timing, so a 300-word wall becomes one unskippable cue.
- **Sections are chapters.** Give them titles under 45 characters that read
  well in a chapter list. Aim for at least three sections over 45 seconds each,
  or the episode gets no chapter track.
- **`factual: true`** on any section making verifiable claims about real
  systems, companies or numbers — and then `sources[]` is mandatory.
- Leave `id` out entirely. It is allocated at build time.

Match the show's existing voice. Read two or three neighbouring blueprints
first; a coding-prep episode that sounds like a lecture is wrong even if every
gate passes.

## 4. Gate it

```
python3 -m scripts.lib.gates content/blueprints/<show>/<slug>.json
```

Fix every `ERROR`. Judge each `WARN` — a duration warning usually means the
section plan is thin, not that the range is wrong.

## 5. Dry run and show the plan

```
python3 scripts/build_episode.py content/blueprints/<show>/<slug>.json --dry-run
```

This needs no ffmpeg, no API key and no credentials. Show the user the section
table and the estimated duration, and get approval before spending a TTS run.

## 6. Build

```
python3 scripts/build_episode.py content/blueprints/<show>/<slug>.json --no-publish
```

Requires ffmpeg and edge-tts. Writes the MP3, chapters and VTT into `data/`.
Listen-check is the user's call.

Publishing is a separate step — use the `publish` skill. It needs
`CLOUDFLARE_API_TOKEN`, which only exists on the `agent` host and in CI, not on
this Mac (see `docs/UPGRADE-SPEC.md` §0b).

## Don't

- Don't edit `scripts/manifest.json` or `site/manifest.json` by hand.
- Don't pick an episode id yourself.
- Don't add a show by editing `app.js` — use the `show-new` skill.
- Don't re-run TTS to fix a typo in the transcript; fix the blueprint and rebuild.
