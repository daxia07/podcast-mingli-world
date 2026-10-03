import test from 'node:test';import assert from 'node:assert/strict';
test('deploy-only preflight uses read-only calls against existing companion resources',async()=>{
 const original=globalThis.fetch;const oldToken=process.env.CLOUDFLARE_API_TOKEN,oldAccount=process.env.CLOUDFLARE_ACCOUNT_ID;
 process.env.CLOUDFLARE_API_TOKEN='test-only';process.env.CLOUDFLARE_ACCOUNT_ID='test-account';const calls=[];
 try{globalThis.fetch=async(url,options)=>{calls.push({url,method:options.method||'GET'});return new Response(JSON.stringify({success:true,result:url.endsWith('/r2/buckets')?{buckets:[{name:'video-mingli-world-state'}]}:url.endsWith('/domains')?[{name:'video.mingli.world'}]:{name:'video-mingli-world'}}))};await import('../scripts/preflight-existing.mjs?present');assert.equal(calls.length,3);assert.ok(calls.every(c=>c.method==='GET'));assert.ok(calls.every(c=>!c.url.includes('zones')&&!c.url.includes('podcast')));
 globalThis.fetch=async()=>new Response(JSON.stringify({success:true,result:{name:'missing'}}));await assert.rejects(import('../scripts/preflight-existing.mjs?missing'),/missing/);
 }finally{globalThis.fetch=original;if(oldToken===undefined)delete process.env.CLOUDFLARE_API_TOKEN;else process.env.CLOUDFLARE_API_TOKEN=oldToken;if(oldAccount===undefined)delete process.env.CLOUDFLARE_ACCOUNT_ID;else process.env.CLOUDFLARE_ACCOUNT_ID=oldAccount}
});
