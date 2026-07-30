const ACCOUNT_ID = '0629de91516b2b363d1215708eaa5332';
const BUCKET = 'podcast-mingli-world';

async function r2Fetch(key, token) {
  const url = `https://${ACCOUNT_ID}.r2.cloudflarestorage.com/${BUCKET}/${key}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) return null;
  return res;
}

async function r2GetJSON(key, token) {
  const res = await r2Fetch(key, token);
  if (!res) return null;
  return res.json();
}

async function r2GetBytes(key, token) {
  const res = await r2Fetch(key, token);
  if (!res) return null;
  return res.arrayBuffer();
}

module.exports = { r2Fetch, r2GetJSON, r2GetBytes };
