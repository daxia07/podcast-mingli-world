export async function onRequest(context) {
  const { request, env } = context;

  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
      }
    });
  }

  if (request.method === 'POST') {
    try {
      const { episode, rating, date } = await request.json();
      if (!episode || !rating || !date) {
        return new Response('missing fields', { status: 400 });
      }

      const key = `feedback/${date}.json`;
      const existing = await env.FEEDBACK_BUCKET.get(key);
      const data = existing
        ? { ...await existing.json(), [String(episode)]: rating }
        : { [String(episode)]: rating };

      await env.FEEDBACK_BUCKET.put(key, JSON.stringify(data));

      return new Response('ok', {
        headers: { 'Access-Control-Allow-Origin': '*' }
      });
    } catch (e) {
      return new Response('invalid', {
        status: 400,
        headers: { 'Access-Control-Allow-Origin': '*' }
      });
    }
  }

  return new Response('not found', {
    status: 404,
    headers: { 'Access-Control-Allow-Origin': '*' }
  });
}
