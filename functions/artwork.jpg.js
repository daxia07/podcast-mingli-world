// GET /artwork.jpg — podcast cover art from R2.
//
// This was referenced in three places and served by none of them: the RSS
// <itunes:image> (so podcast clients showed no cover), the web app manifest
// icons (so Chrome refused to install the PWA as a real app), and the Media
// Session metadata (so the lock screen had no image). The file has always been
// in R2; nothing routed to it, so the path fell through to the SPA and returned
// index.html with content-type text/html.

export async function onRequest(context) {
  const { env } = context;
  try {
    const obj = await env.FEEDBACK_BUCKET.get('artwork.jpg');
    if (!obj) return new Response('not found', { status: 404 });

    return new Response(obj.body, {
      headers: {
        'Content-Type': 'image/jpeg',
        'Access-Control-Allow-Origin': '*',
        // Cover art changes rarely; a week is a reasonable compromise between
        // freshness and not refetching a 1400x1400 JPEG on every app launch.
        'Cache-Control': 'public, max-age=604800',
        ...(obj.httpEtag ? { ETag: obj.httpEtag } : {}),
      },
    });
  } catch (e) {
    return new Response('not found', { status: 404 });
  }
}
