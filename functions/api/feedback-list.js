// GET /api/feedback-list?prefix=feedback/&cursor=... — list R2 keys.
//
// The one thing the wrangler CLI cannot do, and the reason arrange.py used to
// guess `feedback/{date}_ep{id}.json` filenames across a 7-day window and miss
// anything that didn't match the pattern. The Pages binding can list; this
// exposes that to the pipeline. No new credential involved.
//
// Auth-gated by _middleware.js (not on the public path list) — it enumerates
// bucket contents, so it should not be world-readable.

const ALLOWED_PREFIXES = ['feedback/', 'episodes/', 'transcripts/', 'chapters/', 'boards/'];
const PAGE_SIZE = 1000;

export async function onRequestGet(context) {
  const { env, request } = context;
  const url = new URL(request.url);
  const prefix = url.searchParams.get('prefix') || 'feedback/';
  const cursor = url.searchParams.get('cursor') || undefined;

  // Constrained rather than arbitrary: this endpoint should never become a
  // general bucket browser.
  if (!ALLOWED_PREFIXES.some((p) => prefix === p || prefix.startsWith(p))) {
    return json(400, { error: `prefix must be one of ${ALLOWED_PREFIXES.join(', ')}` });
  }

  try {
    const listing = await env.FEEDBACK_BUCKET.list({ prefix, cursor, limit: PAGE_SIZE });
    return json(200, {
      keys: listing.objects.map((o) => o.key),
      truncated: Boolean(listing.truncated),
      cursor: listing.truncated ? listing.cursor : null,
    });
  } catch (err) {
    return json(500, { error: String(err?.message || err) });
  }
}

function json(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
}
