const fs=require('node:fs');
const {chromium}=require('playwright');
const v='https://velocemercato.fr';
const par=()=>new Date().toLocaleString('sv-SE',{timeZone:'Europe/Paris'});
const brief=s=>s.split('\n').map(l=>l.trim()).filter(l=>/score|matchs|connexion|donn[eé]es|hors.ligne|chargement/i.test(l)).slice(0,13);
(async()=>{
 const b=await chromium.launch();
 const jobs=await Promise.allSettled([
 (async()=>{
  const c=await b.newContext({viewport:{width:390,height:900}});
  try{
   const p=await c.newPage(); const errors=[],feeds=[];
   p.on('pageerror',e=>errors.push(e.message.slice(0,150)));
   p.on('response',r=>{if(/\/scores\.json(?:\?|$)/.test(r.url()))feeds.push(r.status());});
   await p.goto(v+'/foot-amateur/',{waitUntil:'load'});
   await p.evaluate(()=>Promise.race([navigator.serviceWorker.ready,new Promise(r=>setTimeout(r,3000))]));
   const target=await p.goto(v+'/scores/',{waitUntil:'load'});
   const hasScores=()=>p.locator('body').innerText().then(t=>/\b\d+ matchs?\b|scores mis à jour/i.test(t));
   let online=false;
   for(let i=0;i<14;i++){if(await hasScores()){online=true;break;}await new Promise(r=>setTimeout(r,350));}
   const onlineText=brief(await p.locator('body').innerText());
   const controlled=await p.evaluate(()=>!!navigator.serviceWorker.controller);
   await c.setOffline(true);
   const off=await p.reload({waitUntil:'load',timeout:8000});
   let offline=false;
   for(let i=0;i<8;i++){if(await hasScores()){offline=true;break;}await new Promise(r=>setTimeout(r,300));}
   return {online,offline,onlineHttp:target.status(),offlineHttp:off.status(),controlled,onlineText,offlineText:brief(await p.locator('body').innerText()),errors,feeds};
  }finally{await c.close();}
 })(),
 (async()=>{
  const cats=['','cbd','caviste','taxi','garage','dentiste','coiffeur','sante','plombier','electricien','commerce'];
  return await Promise.all(cats.map(async cat=>{
    const p=await b.newPage();
    try{
      const r=await p.goto(v+'/services/'+(cat?'?categorie='+cat:''),{waitUntil:'load'});
      return {cat,http:r.status(),title:await p.title(),canonical:await p.locator('link[rel=canonical]').getAttribute('href'),selected:await p.locator('select').first().inputValue().catch(()=>null)};
    }finally{await p.close();}
  }));
 })(),
 (async()=>{
  return await Promise.all(['/kit-du-jour','/kit-pronos','/demos/coiffeur'].map(async path=>{
   const p=await b.newPage();
   try{const r=await p.goto(v+path,{waitUntil:'domcontentloaded'});
    return {path,http:r.status(),robots:await p.evaluate(()=>document.querySelector('meta[name=robots]')?.content??null),header:(await r.allHeaders())['x-robots-tag']??null};
   }finally{await p.close();}
  }));
 })()
 ]);
 await b.close();
 const o={at:par(),pwa:jobs[0].status==='fulfilled'?jobs[0].value:String(jobs[0].reason),seo:jobs[1].status==='fulfilled'?jobs[1].value:String(jobs[1].reason),robots:jobs[2].status==='fulfilled'?jobs[2].value:String(jobs[2].reason)};
 fs.writeFileSync('evidence/validation-ciblee.json',JSON.stringify(o,null,2));
 console.log('VM_REFINE '+JSON.stringify(o));
})().catch(e=>{console.error(e);process.exitCode=1;});
