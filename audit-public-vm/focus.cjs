const fs=require('node:fs');
const {chromium}=require('playwright');
const V='https://velocemercato.fr', U='https://vmunivers.fr';
const at=()=>new Date().toLocaleString('sv-SE',{timeZone:'Europe/Paris'});
const out={started:at()};
const msg=e=>e.message.split('\n')[0];
const safe=async fn=>{try{return await fn()}catch(e){return {error:msg(e)}}};
const axe=fs.readFileSync(require.resolve('axe-core/axe.min.js'),'utf8');
async function main(){
const b=await chromium.launch();
async function fresh(url,width=390,sw='block',wait='load'){
 const p=await b.newPage({viewport:{width,height:900},serviceWorkers:sw});
 const r=await p.goto(url,{waitUntil:wait,timeout:18000});
 return [p,r];
}
const close=async(p,fn)=>{try{return await fn()}finally{await p.close();}};
const normalize=s=>s.normalize('NFKD').replace(/\p{M}/gu,'').replace(/[’']/g,"'").replace(/\s+/g,' ').trim().toLowerCase();
const timeParts=s=>s?.match(/T(\d\d):(\d\d)/)?.slice(1);
const jobs={
 advice:async()=>{
   const r=await fetch(V+'/pronos/selection.json',{signal:AbortSignal.timeout(15000)}), j=await r.json(), a=j.publicAdvice;
   const one=async(path,selectors)=>{const [p,res]=await fresh(V+path);return close(p,async()=>{
     const d=await p.evaluate(selectors=>{
       const el=selectors.map(s=>document.querySelector(s)).find(Boolean);
       return {anchor:!!document.getElementById('pronos-du-jour'),block:!!el,tag:el?.tagName??null,heading:el?.querySelector('h2,h3')?.innerText??null,
         text:el?.innerText??'',sources:[...el?.querySelectorAll('a[href^="https:"]')??[]].map(e=>e.href)};
     },selectors);
     const n=normalize(d.text);
     const legacy=/\bcote totale\b|\bcote relevee\b|\bparis combines?\b|\bcombin[eé] public\b|\bprobabilite indiquee\b/.test(n);
     const matchTokens=a?.match?.split(/[–—]/).map(x=>normalize(x.split('·')[0]).trim())??[];
     const h=timeParts(a?.kickoff);
     return {http:res.status(),url:p.url(),anchor:d.anchor,block:d.block,tag:d.tag,heading:d.heading,hasLegacyContent:legacy,
       exactAnalysis:!!a?.analysis&&n.includes(normalize(a.analysis)),match:matchTokens.length>0&&matchTokens.every(x=>n.includes(x)),
       kickoff:!!h&&(n.includes(h.join(':'))||n.includes(h.join(' h '))),sourceCount:d.sources.length,sourceMatches:(a?.sources??[]).filter(s=>d.sources.includes(s.url)).length,
       emptyState:/aucune analyse|pas de conseil|aucun conseil/.test(n),textLength:d.text.length};
   });};
   const [home,dedicated]=await Promise.all([one('/', ['#pronos-du-jour','#pronos','#prono']),one('/pronos/#pronos-du-jour',['#pronos-du-jour','#conseil-contenu'])]);
   return {jsonHttp:r.status,active:!!a?.kickoff&&Date.parse(a.kickoff)>Date.now(),match:a?.match,kickoff:a?.kickoff,publishedAt:a?.publishedAt,sources:a?.sources?.length??0,legacyJson:Array.isArray(j.combines)?j.combines.length:null,home,dedicated};
 },
 video:async()=>{
   const routes=['/','/gaming','/soutenir','/archives','/studio','/ou-regarder','/multisport/','/foot-amateur/','/web-studio','/actus/'];
   const refs=await Promise.all(routes.map(async path=>{const [p,r]=await fresh(V+path,390,'block','domcontentloaded');return close(p,async()=>({path,http:r.status(),links:await p.evaluate(()=>[...document.querySelectorAll('a')].filter(x=>/vid[eé]os|pastilles/i.test(x.textContent)||/#videos$/.test(x.href)).filter(x=>!!x.getClientRects().length).map(x=>[x.textContent.trim().slice(0,44),x.href]).slice(0,15))}));}));
   const dest=await Promise.all(['/#videos','/studio'].map(async path=>{const [p,r]=await fresh(V+path);return close(p,async()=>({path,http:r.status(),url:p.url(),anchor:await p.locator('[id=videos],a[name=videos]').count(),title:await p.title()}));}));
   return {refs,dest};
 },
 gaming:async()=>{
   const paths=['/pronos/','/vm-gaming/'];
   return await Promise.all(paths.map(async path=>{const [p,r]=await fresh(V+path);return close(p,async()=>{
     const links=await p.evaluate(()=>[...document.querySelectorAll('a[href]')].filter(a=>/gameblog\.fr|Source originale/i.test(a.href+' '+a.innerText)).map(a=>({url:a.href,label:a.innerText.trim()})));
     const bad=links.filter(a=>/https?:\/\/[^/]+\/https?:\/\//i.test(a.url));
     const selected=[...new Set([...bad,...links.filter(x=>/gameblog\.fr/.test(x.url))].map(a=>a.url))].slice(0,12);
     const statuses=await Promise.all(selected.map(url=>safe(async()=>{const x=await p.request.get(url,{timeout:10000});return [url,x.status(),x.url()];})));
     return {path,http:r.status(),samples:links.length,bad:bad.map(x=>x.url),statuses};
   });}));
 },
 responsive:async()=>{
   const routes=[V+'/',V+'/multisport/nba/',V+'/foot-amateur/',V+'/foot-amateur/?region=GES',V+'/belfort/',U+'/'];
   return await Promise.all(routes.map(async url=>[url,await Promise.all([320,390,768].map(width=>safe(async()=>{
     const [p,r]=await fresh(url,width);return close(p,async()=>({width,http:r.status(),...await p.evaluate(()=>({doc:document.documentElement.scrollWidth,client:document.documentElement.clientWidth,body:document.body.scrollWidth}))}));
   })))]));
 },
 pwa:async()=>{
   const [p,r]=await fresh(V+'/',390,'allow');
   const info=()=>p.evaluate(async()=>({url:location.href,manifest:document.querySelector('link[rel=manifest]')?.getAttribute('href')??null,controlled:!!navigator.serviceWorker.controller,registrations:(await navigator.serviceWorker.getRegistrations()).length}));
   return close(p,async()=>{
     const root=await info();
     const a=await p.goto(V+'/foot-amateur/',{waitUntil:'load',timeout:10000});
     await p.evaluate(()=>Promise.race([navigator.serviceWorker.ready,new Promise(r=>setTimeout(r,2500))]));
     const foot=await info();
     const x=await p.goto(V+'/scores/',{waitUntil:'load',timeout:10000});
     const before={...(await info()),http:x.status(),scoreRows:await p.locator('[data-match-id],.match-card,.match-row').count()};
     const scoreText=await p.locator('body').innerText();
     before.scoresRendered=/\d+ matchs|scores mis à jour/i.test(scoreText);
     await p.context().setOffline(true);
     const offline=await safe(async()=>{const q=await p.reload({waitUntil:'domcontentloaded',timeout:6000});const t=await p.locator('body').innerText({timeout:2500});return {http:q?.status(),scoresRendered:/\d+ matchs|scores mis à jour/i.test(t),heading:await p.locator('h1').first().innerText({timeout:2500})};});
     return {root,foot,before,offline};
   });
 },
 seo:async()=>{
   const unpack=s=>[...s.matchAll(/<loc>\s*([^<]+)\s*<\/loc>/g)].map(m=>m[1].trim().replaceAll('&amp;','&'));
   const clean=(url,base)=>{try{const u=new URL(url,base);u.hash='';return u.href;}catch{return null;}};
   const attr=(tag,n)=>tag.match(new RegExp('\\b'+n+'\\s*=\\s*["\']([^"\']+)["\']','i'))?.[1];
   async function read(url){return safe(async()=>{const r=await fetch(url,{signal:AbortSignal.timeout(9000)});if(!r.ok||!r.headers.get('content-type')?.includes('html'))return {url,final:r.url,http:r.status};const h=await r.text();return {url,final:r.url,http:r.status,title:h.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]?.trim()??null,canonical:[...h.matchAll(/<link\b[^>]*>/gi)].map(m=>m[0]).filter(t=>attr(t,'rel')?.toLowerCase()==='canonical').map(t=>attr(t,'href')),links:[...h.matchAll(/<a\b[^>]*>/gi)].map(m=>clean(attr(m[0],'href')||'',r.url)).filter(x=>x&&x.startsWith(V+'/')&&!/[?]|\.(?:jpg|png|svg|json|mp4|pdf)$/i.test(x)&&!/\/cdn-cgi\/|\/atelier|\/admin|\/api\//i.test(x))};});}
   const bounded=async(urls)=>{let result=[];for(let i=0;i<urls.length;i+=14)result.push(...await Promise.all(urls.slice(i,i+14).map(read)));return result;};
   const map=await fetch(V+'/sitemap.xml',{signal:AbortSignal.timeout(10000)});
   const loc=unpack(await map.text()).filter(x=>x.startsWith(V+'/'));
   const seen=new Set([V+'/',V+'/services/',...loc]);let all=await bounded([...seen]);
   for(let depth=0;depth<2;depth++){const q=[...new Set(all.flatMap(r=>r.links??[]))].filter(x=>!seen.has(x)).slice(0,280-seen.size);if(!q.length)break;q.forEach(x=>seen.add(x));all.push(...await bounded(q));}
   const h=new Map(all.filter(x=>x.http===200&&x.links).map(x=>[x.final,x]));
   const pages=[...h.values()];const services=pages.filter(x=>new URL(x.final).pathname.startsWith('/services/')).map(x=>[new URL(x.final).pathname,x.title,x.canonical]);
   return {sitemap:loc.length,requests:all.length,errors:all.filter(x=>x.error).length,pages:pages.length,noCanonical:pages.filter(x=>!x.canonical.length).map(x=>x.final),multipleCanonical:pages.filter(x=>x.canonical.length>1).map(x=>x.final),services,serviceUniqueTitles:new Set(services.map(x=>x[1])).size};
 },
 a11y:async()=>{
  return await Promise.all(['/','/actus/','/vm-gaming/','/multisport/nba/','/services/','/pronos/'].map(path=>safe(async()=>{
   const [p,r]=await fresh(V+path);return close(p,async()=>{
     await p.addScriptTag({content:axe});const x=await p.evaluate(async()=>await axe.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
     return {path,http:r.status(),violations:x.violations.map(v=>[v.id,v.nodes.length]),incomplete:x.incomplete.map(v=>v.id)};
   });
  })));
 },
 portal:async()=>{const [p,r]=await fresh(U+'/');return close(p,async()=>({http:r.status(),url:p.url(),title:await p.title(),directory:await p.getByText(/annuaire/i).count()}));}
};
try{
 const phases=[['advice','video','gaming','portal'],['responsive','pwa'],['seo','a11y']];
 for(const phase of phases)await Promise.all(phase.map(async key=>{out[key]=await safe(jobs[key]);console.log('VM_FINAL_'+key.toUpperCase()+' '+JSON.stringify(out[key]));}));
}finally{await b.close();}
out.finished=at();fs.writeFileSync('evidence/validation-finale.json',JSON.stringify(out,null,2));console.log('VM_FINAL_TIME '+out.started+' / '+out.finished);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
