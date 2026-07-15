const COOKIE_NAME = 'mingli_auth';

async function computeToken(authSecret) {
  const AUTH_USER = 'ming';
  const AUTH_PASS = 'ping';
  const data = new TextEncoder().encode(`${AUTH_USER}:${AUTH_PASS}:${authSecret}`);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function validateToken(token, authSecret) {
  if (!token) return false;
  const expected = await computeToken(authSecret);
  return token === expected;
}

const LOGIN_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no,maximum-scale=1">
<title>Sign In</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{min-height:100vh;display:flex;align-items:center;justify-content:center;background:#f5f5f5;font-family:system-ui,-apple-system,sans-serif}
.card{background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);padding:32px;width:100%;max-width:360px}
.logo{text-align:center;margin-bottom:24px}
.logo h1{font-size:24px;color:#4b4b4b;font-weight:700}
.logo p{font-size:14px;color:#999;margin-top:4px}
label{display:block;font-size:14px;font-weight:600;color:#4b4b4b;margin-bottom:6px}
input{width:100%;padding:10px 14px;border:2px solid #e0e0e0;border-radius:12px;font-size:15px;outline:none;transition:border .2s}
input:focus{border-color:#58cc02}
.form-group{margin-bottom:16px}
button{width:100%;padding:12px;background:#58cc02;color:#fff;border:none;border-radius:12px;font-size:16px;font-weight:700;cursor:pointer;transition:background .2s}
button:hover{background:#46a302}
button:disabled{opacity:.5;cursor:not-allowed}
.error{font-size:13px;color:#d32f2f;background:#fde8e8;border-radius:8px;padding:8px 12px;margin-bottom:12px}
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <h1>Mingli</h1>
    <p>Sign in to continue</p>
  </div>
  <div id="error" style="display:none" class="error"></div>
  <form id="loginForm">
    <div class="form-group">
      <label for="username">Username</label>
      <input id="username" type="text" autocomplete="username" required>
    </div>
    <div class="form-group">
      <label for="password">Password</label>
      <input id="password" type="password" autocomplete="current-password" required>
    </div>
    <button type="submit" id="submitBtn">Sign In</button>
  </form>
</div>
<script>
document.getElementById('loginForm').addEventListener('submit', async(e)=>{
  e.preventDefault();
  const btn=document.getElementById('submitBtn');
  const errEl=document.getElementById('error');
  btn.disabled=true;btn.textContent='Signing in...';errEl.style.display='none';
  try{
    const res=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:document.getElementById('username').value,password:document.getElementById('password').value})});
    if(res.ok){window.location.reload();return}
    const data=await res.json();
    errEl.textContent=data.error||'Login failed';errEl.style.display='block';
  }catch{errEl.textContent='Network error';errEl.style.display='block'}
  finally{btn.disabled=false;btn.textContent='Sign In'}
});
</script>
</body>
</html>`;

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const pathname = url.pathname;

  const authSecret = env.AUTH_SECRET || 'tutor-local-dev';

  if (pathname === '/api/login' && request.method === 'POST') {
    try {
      const body = await request.json();
      const { username, password } = body;
      if (!username || !password) {
        return new Response(JSON.stringify({ error: 'Username and password required' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (username !== 'ming' || password !== 'ping') {
        return new Response(JSON.stringify({ error: 'Invalid credentials' }), {
          status: 401,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      const token = await computeToken(authSecret);
      const cookieDomain = env.COOKIE_DOMAIN || undefined;
      const cookieParts = [
        `${COOKIE_NAME}=${token}`,
        'Path=/',
        'Max-Age=31536000',
        'HttpOnly',
        'SameSite=lax',
        'Secure',
      ];
      if (cookieDomain) cookieParts.push(`Domain=${cookieDomain}`);
      return new Response(JSON.stringify({ success: true }), {
        headers: {
          'Content-Type': 'application/json',
          'Set-Cookie': cookieParts.join('; '),
        },
      });
    } catch {
      return new Response(JSON.stringify({ error: 'Invalid request' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  }

  if (pathname === '/api/logout' && request.method === 'POST') {
    const cookieDomain = env.COOKIE_DOMAIN || undefined;
    const cookieParts = [`${COOKIE_NAME}=`, 'Path=/', 'Max-Age=0', 'HttpOnly', 'SameSite=lax'];
    if (cookieDomain) cookieParts.push(`Domain=${cookieDomain}`);
    return new Response(JSON.stringify({ success: true }), {
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': cookieParts.join('; '),
      },
    });
  }

  if (pathname === '/login' || pathname.startsWith('/login/')) {
    const cookieHeader = request.headers.get('Cookie') || '';
    const match = cookieHeader.match(new RegExp(`${COOKIE_NAME}=([^;]+)`));
    const token = match ? match[1] : null;
    if (await validateToken(token, authSecret)) {
      return Response.redirect(new URL('/', request.url).href, 302);
    }
    return new Response(LOGIN_HTML, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    });
  }

  const cookieHeader = request.headers.get('Cookie') || '';
  const match = cookieHeader.match(new RegExp(`${COOKIE_NAME}=([^;]+)`));
  const token = match ? match[1] : null;

  if (!(await validateToken(token, authSecret))) {
    if (pathname.startsWith('/api/')) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    return Response.redirect(new URL('/login', request.url).href, 307);
  }

  return next();
}
