// GET /chapters/:file — Podcasting 2.0 chapter document from R2.
//
// Public (whitelisted in _middleware.js) because RSS <podcast:chapters> links
// here and podcast clients fetch it with no auth cookie.
//
// These were being uploaded but never served: without this Function the path
// fell through to the SPA and returned index.html, which the player then failed
// to parse as JSON.

export async function serveArtifact(context, prefix, contentType) {
  const { env, params } = context;
  try {
    const obj = await env.FEEDBACK_BUCKET.get(`${prefix}/${params.file}`);
    if (!obj) return new Response('not found', { status: 404 });

    return new Response(obj.body, {
      headers: {
        'Content-Type': contentType,
        'Access-Control-Allow-Origin': '*',
        // Regenerated whenever an episode is rebuilt, so a day rather than the
        // immutable year the audio gets.
        'Cache-Control': 'public, max-age=86400',
        ...(obj.httpEtag ? { ETag: obj.httpEtag } : {}),
      },
    });
  } catch (e) {
    return new Response('not found', { status: 404 });
  }
}

export async function onRequest(context) {
  return serveArtifact(context, 'chapters', 'application/json+chapters');
}
