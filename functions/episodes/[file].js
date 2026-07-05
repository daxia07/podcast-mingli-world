export async function onRequest(context) {
  const { env, params } = context;
  const filename = params.file;
  try {
    const key = `episodes/${filename}`;
    const obj = await env.FEEDBACK_BUCKET.get(key);
    if (!obj) {
      return new Response('not found', { status: 404 });
    }
    return new Response(obj.body, {
      headers: {
        'Content-Type': 'audio/mpeg',
        'Accept-Ranges': 'bytes',
        'Access-Control-Allow-Origin': '*'
      }
    });
  } catch (e) {
    return new Response('not found', { status: 404 });
  }
}
