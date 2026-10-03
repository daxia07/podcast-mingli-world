import {chromium} from '/Users/daxia/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import {existingCredentials} from './verify-live.mjs';
import fs from 'node:fs';
const live=process.env.AUDIT_LIVE==='1',base=live?'https://video.mingli.world':'http://localhost:4174',prefix=live?'phone-live-before':'phone-candidate';
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--no-sandbox']});
const results=[];
try{for(const size of [{width:320,height:568},{width:390,height:844},{width:390,height:664},{width:1440,height:900}]){
 const ctx=await browser.newContext({viewport:size,isMobile:size.width<600,hasTouch:true});const p=await ctx.newPage();
 // Audit starts from a fresh isolated profile and never changes the live owner profile.
 await p.route('**/api/profile',r=>r.fulfill({status:200,contentType:'application/json',headers:{'X-Profile-Version':'"audit"'},body:JSON.stringify({state:null})}));
 await p.goto(base);const c=live?existingCredentials():{username:'fixture',password:'fixture-only'};await p.locator('#username').fill(c.username);await p.locator('#password').fill(c.password);await p.getByRole('button',{name:'Sign in',exact:true}).click();await p.locator('.idea').first().waitFor();
 const geometry=await p.evaluate(()=>{const f=document.querySelector('#feed'),a=f.firstElementChild,b=a.getBoundingClientRect();return {viewport:innerHeight,feed:f.clientHeight,card:a.clientHeight,cardOverflow:a.scrollHeight-a.clientHeight,pageOverflow:document.documentElement.scrollHeight-innerHeight,snap:getComputedStyle(f).scrollSnapType,actions:[...a.querySelectorAll('.actions button')].map(x=>{const r=x.getBoundingClientRect();return {name:x.textContent,height:r.height,bottom:r.bottom,visible:r.bottom<=b.bottom&&r.top>=b.top}}),media:a.querySelector('.media').getBoundingClientRect().toJSON()}});
 await p.screenshot({path:`evidence/${prefix}-${size.width}-${size.height}.png`});results.push({size,geometry});await ctx.close();
}}finally{await browser.close();fs.writeFileSync(`evidence/${prefix}.json`,JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2))}
