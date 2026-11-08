const fs=require('node:fs');
const {chromium}=require('playwright');
const base='https://velocemercato.fr';
const routes=['/','/actus/','/multisport/nba/','/vm-gaming/','/foot-amateur/','/belfort/','/scores/','/pronos/','/web-studio#devis','/pub/','/regions/evenements/','/kit-du-jour','/menu/'];
async function audit(){
 const b=await chromium.launch();const results={at:new Date().toLocaleString('sv-SE',{timeZone:'Europe/Paris'}),axe:[],flows:[]};
 const flow=(id,data)=>results.flows.push({id,data});
 const fresh=async(route,options={})=>{const c=await b.newContext({viewport:{width:390,height:900},...options});const p=await c.newPage();await p.goto(base+route,{waitUntil:'load',timeout:15000});return [c,p];};
 await Promise.all(routes.map(async route=>{
   const [c,p]=await fresh(route,{serviceWorkers:'block'});
   try{
     await p.addScriptTag({content:fs.readFileSync(require.resolve('axe-core/axe.min.js'),'utf8')});
     const x=await p.evaluate(async()=>await axe.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
     results.axe.push({route,violations:x.violations.map(v=>({id:v.id,impact:v.impact,count:v.nodes.length,sample:v.nodes.slice(0,2).map(n=>n.target.join(' '))})),incomplete:x.incomplete.map(v=>v.id)});
   }catch(e){results.axe.push({route,error:e.message.split('\n')[0]});}finally{await c.close();}
 }));
 const browserTests=[
  ['home',async()=>{
    const [c,p]=await fresh('/');
    try{
      const ui=await p.evaluate(()=>({title:document.title,pwa:[...document.querySelectorAll('link[rel=manifest]')].map(e=>e.href),scripts:[...document.scripts].map(e=>e.src).filter(Boolean),skip:[...document.querySelectorAll('a[href^="#"]')].find(e=>/aller au contenu|aller aux actualit/i.test(e.textContent))?.textContent??null,media:document.querySelectorAll('video,iframe[src*=youtube]').length,navEntries:[...document.querySelectorAll('[aria-label="Nos sports"] a, [aria-label="Catégories"] a')].map(e=>[e.textContent.trim(),e.getAttribute('href')])}));
      const focus=[];
      for(let i=0;i<8;i++){await p.keyboard.press('Tab');focus.push(await p.evaluate(()=>{const a=document.activeElement,s=getComputedStyle(a);return [a.tagName,a.textContent.trim().slice(0,50),s.outlineStyle,s.outlineWidth];}));}
      return {...ui,focus};
    }finally{await c.close();}
  }],
  ['video_anchor',async()=>{
    const [c,p]=await fresh('/gaming',{serviceWorkers:'block'});
    try{
     const menu=p.locator('a[href="/#videos"]').first();
     const href=await menu.getAttribute('href');
     const res=await p.goto(new URL(href,base).href,{waitUntil:'load'});
     return {from:base+'/gaming',href,dest:p.url(),http:res.status(),hasTarget:await p.locator('[id="videos"],a[name="videos"]').count(),heading:await p.locator('h1').first().innerText()};
    }finally{await c.close();}
  }],
  ['evenements',async()=>{
    const [c,p]=await fresh('/regions/evenements/',{serviceWorkers:'block'});
    try{
      const anchors=await p.evaluate(()=>[...document.querySelectorAll('a[href^="#"]')].map(a=>[a.getAttribute('href'),!!document.getElementById(a.hash.slice(1)),a.textContent.trim().slice(0,70)]));
      const links=anchors.filter(a=>['#brocantes','#marches','#concerts','#soirees','#loto','#matchs','#theatre','#salons'].includes(a[0]));
      const el=p.locator('a[href="#brocantes"]').first();
      await el.click({timeout:3000});return {links,url:p.url(),scroll:await p.evaluate(()=>window.scrollY)};
    }finally{await c.close();}
  }],
  ['contact',async()=>{
    const [c,p]=await fresh('/pub/',{serviceWorkers:'block'});
    try{
      const mail=await p.evaluate(()=>({technical:[...document.querySelectorAll('a[href*="/cdn-cgi/l/email-protection"]')].map(a=>a.textContent.trim()),mailto:[...document.querySelectorAll('a[href^="mailto:"]')].map(a=>a.textContent.trim())}));
      return mail;
    }finally{await c.close();}
  }],
  ['devis',async()=>{
    const [c,p]=await fresh('/web-studio#devis',{serviceWorkers:'block'});
    try{
      return await p.locator('form').first().evaluate(f=>({method:f.method,actionHost:new URL(f.action).hostname,initialValid:f.checkValidity(),required:[...f.querySelectorAll('[required]')].map(e=>e.name),honeypot:!!f.querySelector('[name=_honey]'),next:!!f.querySelector('[name=_next]')}));
    }finally{await c.close();}
  }],
  ['pwa',async()=>{
    const [c,p]=await fresh('/');
    try{
     const get=()=>p.evaluate(async()=>({url:location.href,manifest:document.querySelector('link[rel=manifest]')?.getAttribute('href')??null,registrations:(await navigator.serviceWorker.getRegistrations()).map(r=>r.scope),controlled:!!navigator.serviceWorker.controller}));
     const home=await get();
     await p.goto(base+'/foot-amateur/',{waitUntil:'load',timeout:10000});
     const foot=await get();
     await p.goto(base+'/scores/',{waitUntil:'load',timeout:10000});
     const scores=await get();
     await c.setOffline(true);
     let offline;
     try{const r=await p.reload({waitUntil:'domcontentloaded',timeout:4500});offline={status:r?.status(),heading:await p.locator('h1').first().innerText({timeout:2500})};}catch(e){offline={error:e.message.split('\n')[0]};}
     return {home,foot,scores,offline};
    }finally{await c.close();}
  }]
 ];
 await Promise.all(browserTests.map(async ([id,test])=>{try{flow(id,await test());}catch(e){flow(id,{error:e.message.split('\n')[0]});}}));
 await b.close();
 fs.writeFileSync('evidence/focus.json',JSON.stringify(results,null,2));console.log('VM_FOCUS '+JSON.stringify(results));
}
audit().catch(e=>{console.error(e);process.exitCode=1;});
