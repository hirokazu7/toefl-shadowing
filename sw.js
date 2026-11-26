// オフライン用：ネットにつながる時は常に最新を取り、つながらない時だけ保存した物を使う
const C='shd-offline';
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;
 e.respondWith((async()=>{const cache=await caches.open(C);const key=u.origin+u.pathname;
  try{const r=await fetch(e.request);if(r.status===200&&await cache.match(key))cache.put(key,r.clone());return r}
  catch(err){const m=await cache.match(key)||(u.pathname.endsWith('/')?await cache.match(key+'index.html'):null);if(m)return m;throw err}})())});
