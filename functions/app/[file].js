// GET /app/:file — serve the sideloadable APK from R2.
//
// Public: the phone downloads this in a browser with no session, and Android's
// package installer re-fetches it. Content-Type matters — served as text/html
// (the SPA fallback, which is what an unrouted path does here) Android refuses
// to treat the download as an installable package.

export async function onRequest(context) {
  const { env, params } = context;
  try {
    const obj = await env.FEEDBACK_BUCKET.get(`app/${params.file}`);
    if (!obj) return new Response('not found', { status: 404 });

    return new Response(obj.body, {
      headers: {
        'Content-Type': 'application/vnd.android.package-archive',
        'Content-Disposition': `attachment; filename="${params.file}"`,
        // Each build replaces this key, so it must not be cached hard.
        'Cache-Control': 'public, max-age=300',
        ...(obj.httpEtag ? { ETag: obj.httpEtag } : {}),
      },
    });
  } catch (e) {
    return new Response('not found', { status: 404 });
  }
}
