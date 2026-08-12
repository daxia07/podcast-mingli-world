// GET /episodes/:file — stream an episode MP3 out of R2.
//
// Range support matters here: episodes run to 100 MB / 60 min, and the player
// seeks by chapter. Without it every seek refetches from byte 0.

// NOT immutable: episodes get rebuilt in place when a bug is fixed, and
// `immutable` tells browsers never to revalidate — a broken build then plays
// from cache for a year no matter what the server has. must-revalidate still
// costs nothing on a hit, because the ETag turns it into a 304.
const EPISODE_CACHE = 'public, max-age=3600, must-revalidate';

/** Classify a `Range` header against a known object size.
 *
 *  RFC 9110 draws a line this function preserves: a range that is merely
 *  *invalid* (inverted bounds, multi-range, unknown unit) must be ignored and
 *  the whole body served, while one that is *unsatisfiable* (starts at or past
 *  EOF) must be rejected with 416.
 *
 *  Returns 'none' | 'ignore' | 'unsatisfiable' | {offset, length}. */
export function classifyRange(header, size) {
  if (!header || size == null) return 'none';

  const match = /^bytes=(\d*)-(\d*)$/.exec(header.trim());
  if (!match) return 'ignore'; // multi-range, other units, junk

  const [, rawStart, rawEnd] = match;

  if (rawStart === '') {
    // Suffix form: `bytes=-500` means the final 500 bytes.
    const suffix = parseInt(rawEnd, 10);
    if (!Number.isFinite(suffix)) return 'ignore';
    if (suffix === 0) return 'unsatisfiable';
    const length = Math.min(suffix, size);
    return { offset: size - length, length };
  }

  const start = parseInt(rawStart, 10);
  if (!Number.isFinite(start)) return 'ignore';
  if (start >= size) return 'unsatisfiable';

  const end = rawEnd === '' ? size - 1 : Math.min(parseInt(rawEnd, 10), size - 1);
  if (!Number.isFinite(end)) return 'ignore';
  if (end < start) return 'ignore';

  return { offset: start, length: end - start + 1 };
}

/** Offset math only — {offset, length} or null. */
export function parseRange(header, size) {
  const result = classifyRange(header, size);
  return typeof result === 'string' ? null : result;
}

export async function onRequest(context) {
  const { env, params, request } = context;
  const key = `episodes/${params.file}`;

  try {
    // HEAD only needs metadata — don't pull the body out of R2 for it.
    if (request.method === 'HEAD') {
      const head = await env.FEEDBACK_BUCKET.head(key);
      if (!head) return new Response('not found', { status: 404 });
      return new Response(null, { status: 200, headers: baseHeaders(head) });
    }

    const rangeHeader = request.headers.get('Range');

    // One round trip when there's no Range; otherwise head first so the range
    // can be validated against the real size before asking for bytes.
    if (!rangeHeader) {
      const obj = await env.FEEDBACK_BUCKET.get(key);
      if (!obj) return new Response('not found', { status: 404 });
      return new Response(obj.body, { status: 200, headers: baseHeaders(obj) });
    }

    const head = await env.FEEDBACK_BUCKET.head(key);
    if (!head) return new Response('not found', { status: 404 });

    const range = classifyRange(rangeHeader, head.size);

    if (range === 'unsatisfiable') {
      return new Response('range not satisfiable', {
        status: 416,
        headers: { 'Content-Range': `bytes */${head.size}`, 'Accept-Ranges': 'bytes' },
      });
    }

    if (typeof range === 'string') {
      // 'none' or 'ignore' — serve the whole body.
      const obj = await env.FEEDBACK_BUCKET.get(key);
      if (!obj) return new Response('not found', { status: 404 });
      return new Response(obj.body, { status: 200, headers: baseHeaders(obj) });
    }

    const obj = await env.FEEDBACK_BUCKET.get(key, { range });
    if (!obj) return new Response('not found', { status: 404 });

    const end = range.offset + range.length - 1;
    const headers = baseHeaders(head);
    headers['Content-Range'] = `bytes ${range.offset}-${end}/${head.size}`;
    headers['Content-Length'] = String(range.length);

    return new Response(obj.body, { status: 206, headers });
  } catch (e) {
    return new Response('not found', { status: 404 });
  }
}

function baseHeaders(obj) {
  const headers = {
    'Content-Type': 'audio/mpeg',
    'Accept-Ranges': 'bytes',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Expose-Headers': 'Content-Range, Content-Length, Accept-Ranges',
    'Cache-Control': EPISODE_CACHE,
  };
  if (obj?.size != null) headers['Content-Length'] = String(obj.size);
  if (obj?.httpEtag) headers['ETag'] = obj.httpEtag;
  return headers;
}
