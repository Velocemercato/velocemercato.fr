import {validateBrief,generateSite,validateSite,applyChatEdit,contentReadiness} from './generator.js';
import {renderSite} from './render.js';
import {PACKS} from './pricing.js';
// Runs synchronously within the existing Atelier Durable Object. No paid API calls.
export function creatorOperation(store,a,now=Date.now()){
 const fail=(status,error)=>({status,body:{error}}),ok=(body,status=200)=>({status,body});
 const view=p=>({id:p.id,version:p.version,site:p.site,used:p.used,approved:p.approved===p.version,quote:p.quote,status:p.status,messages:p.messages});
 if(a.action==='create'){
  const valid=validateBrief(a.body);if(!valid.ok)return fail(400,valid.errors.join(', '));
  const key='creator-quota:'+new Date(now).toISOString().slice(0,10)+':'+a.ipHash;
  const n=store.get(key)||0;if(n>=3)return fail(429,'Trois projets gratuits par jour maximum.');
  const p={id:crypto.randomUUID(),owner:a.tokenHash,site:generateSite(a.body),version:1,used:0,approved:0,quote:null,messages:[],status:'draft',created:now};
  store.put(key,n+1);store.put('creator:'+p.id,p);return ok(view(p),201);
 }
 if(a.action==='list')return a.admin?ok(store.list('creator:').map(p=>({id:p.id,name:p.site.name||p.id,status:p.status,version:p.version,created:p.created}))):fail(403,'Accès administrateur requis.');
 const p=store.get('creator:'+a.id);if(!p||(!a.admin&&p.owner!==a.tokenHash))return fail(404,'Projet introuvable.');
 const save=()=>{store.put('creator:'+p.id,p);return ok(view(p))};
 if(a.action==='get')return ok(view(p));
 if(a.action==='preview'){
  const files=renderSite(p.site,{preview:true}),page=a.page||'index.html';
  return files[page]?{status:200,html:files[page],mime:page.endsWith('.css')?'text/css; charset=utf-8':'text/html; charset=utf-8'}:fail(404,'Page introuvable.');
 }
 if(a.action==='edit'){
  if(p.used>=10)return fail(429,'Limite gratuite de dix modifications atteinte.');
  const text=String(a.body?.text||'').trim().slice(0,400);if(!text)return fail(400,'Message vide.');
  const r=applyChatEdit(p.site,text);
  if(r.changed){if(!validateSite(r.site,[]).ok)return fail(400,'Modification invalide.');p.site=r.site;p.version++;p.used++;p.approved=0;p.status='draft';}
  p.messages.push({from:'client',text},{from:'assistant',text:r.reply});p.messages=p.messages.slice(-40);return save();
 }
 if(a.action==='approve'){p.approved=p.version;return save()}
 if(a.action==='request-quote'){const pack=PACKS.find(x=>x.id===a.body?.pack);if(!pack)return fail(400,'Offre inconnue.');p.quote={pack:pack.id,label:pack.label,amount:pack.price};p.status='quote_requested';return save()}
 // Preview release: no live payment, export or publication can be enabled by a client or admin.
 if(['publish','export','payment'].includes(a.action))return fail(403,'Version de recette : paiement, export et publication désactivés.');
 return fail(404,'Action inconnue.');
}
