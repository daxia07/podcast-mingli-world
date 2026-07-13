var CACHE_V='interview-en-v2';
var SHELL=['/','/style.css','/app.js','/manifest.json','/manifest.webmanifest'];
var AUDIO_CACHE='interview-audio-v2';

self.addEventListener('install',function(e){
  e.waitUntil(caches.open(CACHE_V).then(function(c){return c.addAll(SHELL);}).then(function(){return self.skipWaiting();}));
});

self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k!==CACHE_V&&k!==AUDIO_CACHE;}).map(function(k){return caches.delete(k);}));
  }).then(function(){return self.clients.claim();}));
});

self.addEventListener('fetch',function(e){
  var url=new URL(e.request.url);
  if(e.request.method!=='GET')return;

  if(url.pathname.endsWith('.mp3')){
    e.respondWith(audioFetch(e.request));
    return;
  }

  if(isShell(url.pathname)){
    e.respondWith(staleWhileRevalidate(e.request));
    return;
  }

  e.respondWith(networkFirst(e.request));
});

function isShell(path){
  return path==='/'||path==='/index.html'||path==='/style.css'||path==='/app.js'||path==='/manifest.json'||path==='/manifest.webmanifest';
}

function staleWhileRevalidate(req){
  return caches.open(CACHE_V).then(function(c){
    return c.match(req).then(function(cached){
      var fetchPromise=fetch(req).then(function(resp){
        if(resp.ok)c.put(req,resp.clone());
        return resp;
      }).catch(function(){return cached;});
      return cached||fetchPromise;
    });
  });
}

function audioFetch(req){
  return caches.open(AUDIO_CACHE).then(function(c){
    return c.match(req).then(function(cached){
      if(cached)return cached;
      return fetch(req).then(function(resp){
        if(resp.ok){
          c.put(req,resp.clone());
        }
        return resp;
      }).catch(function(){
        return new Response('',{status:503,statusText:'Offline'});
      });
    });
  });
}

function networkFirst(req){
  return fetch(req).then(function(resp){
    if(resp.ok){
      var clone=resp.clone();
      caches.open(CACHE_V).then(function(c){c.put(req,clone);});
    }
    return resp;
  }).catch(function(){
    return caches.match(req);
  });
}

self.addEventListener('message',function(e){
  if(e.data&&e.data.type==='skip-waiting')self.skipWaiting();
});
