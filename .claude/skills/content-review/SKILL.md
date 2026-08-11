---
name: content-review
description: Review an episode blueprint for quality before it is built. Use after drafting an episode and before spending a TTS run.
---

# Review a blueprint

The gates catch mechanical problems. This is the pass that catches bad episodes
that happen to be well-formed.

## 1. Run the mechanical gates first

```
python3 -m scripts.lib.gates content/blueprints/<show>/<slug>.json
python3 scripts/build_episode.py content/blueprints/<show>/<slug>.json --dry-run
```

No point reviewing prose that won't build.

## 2. Read it as audio, not as text

Read every line as if hearing it once, with no ability to scroll back.

- **Does a listener know where they are?** Long stretches without a signpost
  are where people drift. Sections are chapters; if one runs past four minutes
  with no internal marker, it is probably two sections.
- **Is anything unspeakable?** Nested clauses, lists longer than three items,
  anything requiring punctuation to parse.
- **Is the pacing even?** Check the dry-run's section table. One section at
  eight minutes and five at ninety seconds means the plan is off.

## 3. Check it against the show

Read the last three episodes of the same show.

- Repetition: is this reusing the same examples, the same opener, the same
  metaphors? The daily format's fixed template is exactly what the blueprint
  system exists to escape.
- Voice: does it match, or does it read like a different writer?
- Level: is it pitched where the show pitches?

## 4. Check the claims

For every section marked `factual: true`, verify each claim against its
`sources[]` entry. If a claim has no source, either find one, soften it to
opinion, or cut it. Numbers get special attention — a throughput figure that
contradicts a storage figure three sections later is the most common failure.

## 5. Report

Give the user: the estimated duration versus the template range, the pacing
table, anything that would make you skip ahead if you were listening, and any
unsourced claim. Recommend build or revise — don't just list observations.
