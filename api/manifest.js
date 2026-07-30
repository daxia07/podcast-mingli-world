const { r2GetJSON } = require('./r2');

module.exports = async function handler(req, res) {
  const token = process.env.CLOUDFLARE_API_TOKEN;
  if (!token) {
    return res.status(500).json({ episodes: [], error: 'missing token' });
  }
  try {
    const data = await r2GetJSON('manifest.json', token);
    if (!data) {
      return res.status(200).json({ episodes: [] });
    }
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Cache-Control', 'no-cache');
    return res.status(200).json(data);
  } catch (e) {
    return res.status(500).json({ episodes: [], error: 'r2 fetch failed' });
  }
};
