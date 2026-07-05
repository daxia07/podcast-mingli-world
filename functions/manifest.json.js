export async function onRequest(context) {
  const { env } = context;
  try {
    const obj = await env.FEEDBACK_BUCKET.get("manifest.json");
    if (!obj) return new Response("{}", {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
    return new Response(obj.body, {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  } catch (e) {
    return new Response("{}", {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
