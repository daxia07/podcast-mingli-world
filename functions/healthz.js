// GET /healthz — is the data path actually working?
//
// Checks what a status page can't see from the outside: that the R2 binding
// resolves and that manifest.json is present and parseable. A green homepage
// with a broken binding used to look identical to a healthy site.
//
// 200 {"ok":true,...} | 503 {"ok":false,"error":...}

export async function onRequest(context) {
  const { env } = context;
  const started = Date.now();

  const respond = (status, body) =>
    new Response(JSON.stringify({ ...body, ms: Date.now() - started }, null, 2), {
      status,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store',
        'Access-Control-Allow-Origin': '*',
      },
    });

  try {
    if (!env.FEEDBACK_BUCKET) {
      return respond(503, { ok: false, error: 'R2 binding FEEDBACK_BUCKET is not configured' });
    }

    const head = await env.FEEDBACK_BUCKET.head('manifest.json');
    if (!head) {
      return respond(503, { ok: false, error: 'manifest.json missing from R2' });
    }

    // head() proves the object exists; only a read proves it is still valid
    // JSON — a truncated upload passes the first check and fails the second.
    const obj = await env.FEEDBACK_BUCKET.get('manifest.json');
    const manifest = JSON.parse(await obj.text());
    const episodes = Array.isArray(manifest.episodes) ? manifest.episodes.length : 0;

    if (episodes === 0) {
      return respond(503, { ok: false, error: 'manifest parsed but contains no episodes' });
    }

    const latest = manifest.episodes.reduce(
      (best, ep) => (!best || (ep.date || '') > (best.date || '') ? ep : best),
      null
    );

    return respond(200, {
      ok: true,
      episodes,
      playlists: Object.keys(manifest.playlists || {}).length,
      manifestBytes: head.size,
      latestEpisodeDate: latest?.date ?? null,
    });
  } catch (err) {
    return respond(503, { ok: false, error: String(err?.message || err) });
  }
}
