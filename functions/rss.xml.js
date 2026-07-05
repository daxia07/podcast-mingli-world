export async function onRequest(context) {
  const { env } = context;
  try {
    const obj = await env.FEEDBACK_BUCKET.get("rss.xml");
    if (!obj) return new Response("<rss/>", {
      headers: { "Content-Type": "application/rss+xml", "Access-Control-Allow-Origin": "*" }
    });
    return new Response(obj.body, {
      headers: { "Content-Type": "application/rss+xml", "Access-Control-Allow-Origin": "*" }
    });
  } catch (e) {
    return new Response("<rss/>", {
      status: 500,
      headers: { "Content-Type": "application/rss+xml", "Access-Control-Allow-Origin": "*" }
    });
  }
}
