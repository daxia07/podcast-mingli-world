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
<meta name="theme-color" content="#f7f6f3">
<title>Mingli — Sign in</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:#f7f6f3;color:#14161c;
  font-family:"SF Pro Text","Segoe UI",system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased;padding:24px;
}
.card{
  background:#fff;border:1px solid #e4e2db;border-radius:16px;
  box-shadow:0 1px 2px rgba(20,22,28,.04),0 12px 40px rgba(20,22,28,.06);
  padding:36px 32px;width:100%;max-width:380px;
}
.logo{margin-bottom:28px}
.logo .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#2f4f8f;margin-right:10px;vertical-align:middle}
.logo h1{font-size:1.4rem;font-weight:650;letter-spacing:-.03em;display:inline;vertical-align:middle}
.logo p{font-size:.9rem;color:#8b909d;margin-top:10px;font-weight:450;line-height:1.45}
label{display:block;font-size:.8rem;font-weight:600;color:#4a4f5c;margin-bottom:7px;letter-spacing:.01em}
input{
  width:100%;padding:12px 14px;border:1px solid #e4e2db;border-radius:12px;
  font-size:.95rem;outline:none;background:#fff;transition:border-color .15s,box-shadow .15s;
}
input:focus{border-color:#a8b8d8;box-shadow:0 0 0 3px rgba(47,79,143,.12)}
.form-group{margin-bottom:16px}
button{
  width:100%;padding:13px;margin-top:6px;background:#14161c;color:#fff;border:none;
  border-radius:12px;font-size:.95rem;font-weight:600;cursor:pointer;letter-spacing:-.01em;
  transition:opacity .15s;
}
button:hover{opacity:.92}
button:disabled{opacity:.5;cursor:not-allowed}
.error{
  font-size:.82rem;color:#9b1c1c;background:#fdecec;border:1px solid #f5c6c6;
  border-radius:10px;padding:10px 12px;margin-bottom:14px;font-weight:500;
}
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <h1><span class="dot" aria-hidden="true"></span>Mingli</h1>
    <p>Interview prep podcast — sign in to continue</p>
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
    <button type="submit" id="submitBtn">Sign in</button>
  </form>
</div>
<script>
document.getElementById('loginForm').addEventListener('submit', async(e)=>{
  e.preventDefault();
  const btn=document.getElementById('submitBtn');
  const errEl=document.getElementById('error');
  btn.disabled=true;btn.textContent='Signing in…';errEl.style.display='none';
  try{
    const res=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:document.getElementById('username').value,password:document.getElementById('password').value})});
    if(res.ok){window.location.reload();return}
    const data=await res.json();
    errEl.textContent=data.error||'Login failed';errEl.style.display='block';
  }catch{errEl.textContent='Network error';errEl.style.display='block'}
  finally{btn.disabled=false;btn.textContent='Sign in'}
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
