// Proposed deploy-only CI: verify existing resources; never provision or change grants/DNS.
const account=process.env.CLOUDFLARE_ACCOUNT_ID,token=process.env.CLOUDFLARE_API_TOKEN;
if(!account||!token)throw Error('Existing CI credentials required');
async function get(path){const r=await fetch('https://api.cloudflare.com/client/v4'+path,{headers:{Authorization:`Bearer ${token}`}});const d=await r.json();if(!r.ok||!d.success)throw Error('Existing-resource check failed');return d.result}
const base=`/accounts/${account}`;
const project=await get(base+'/pages/projects/video-mingli-world');
if(project.name!=='video-mingli-world')throw Error('Existing companion Pages project missing');
const buckets=await get(base+'/r2/buckets');
if(!buckets.buckets.some(b=>b.name==='video-mingli-world-state'))throw Error('Existing private profile bucket missing; stop without provisioning');
const domains=await get(base+'/pages/projects/video-mingli-world/domains');
if(!domains.some(d=>d.name==='video.mingli.world'))throw Error('Existing domain association missing; stop without modifying DNS');
console.log('Existing companion project, profile bucket and domain verified. No resources created.');
