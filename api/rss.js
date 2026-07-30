const { r2GetBytes } = require('./r2');

module.exports = async function handler(req, res) {
  const token = process.env.CLOUDFLARE_API_TOKEN;
  if (!token) {
    return res.status(500).send('<rss version="2.0"><channel><title>Error</title></channel></rss>');
  }
  try {
    const data = await r2GetBytes('rss.xml', token);
    if (!data) {
      return res.status(200).send('<rss version="2.0"><channel><title>No episodes yet</title></channel></rss>');
    }
    res.setHeader('Content-Type', 'application/rss+xml');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Cache-Control', 'no-cache');
    return res.status(200).send(Buffer.from(data));
  } catch (e) {
    return res.status(500).send('<rss version="2.0"><channel><title>Error</title></channel></rss>');
  }
};
