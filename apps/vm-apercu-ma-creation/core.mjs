const HEADERS={"cache-control":"private, no-store, max-age=0","pragma":"no-cache","expires":"0","x-robots-tag":"noindex, nofollow, noarchive","referrer-policy":"no-referrer","x-content-type-options":"nosniff","x-frame-options":"DENY"};
export function json(data,status=200){return new Response(JSON.stringify(data),{status,headers:{...HEADERS,"content-type":"application/json; charset=utf-8"}})}
export class Consultation {
 constructor(ctx){this.ctx=ctx;this.clock=()=>Date.now()}
 async fetch(request){
  const {operation,ttl}=await request.json();if(!['open','status'].includes(operation))return json({error:'invalid_operation'},400);
  const now=this.clock();
  const record=await this.ctx.storage.transaction(async tx=>{
   let r=await tx.get('window');
   if(!r&&operation==='open'){r={openedAt:now,expiresAt:now+Math.max(1000,Math.min(Number(ttl)||86400000,86400000))};await tx.put('window',r)}
   return r||null;
  });
  if(!record)return json({openedAt:null,expiresAt:null});
  if(now>=record.expiresAt)return json({...record,error:'expired'},410);
  return json(record);
 }
}
function bytes(s){return Uint8Array.from(atob(s.replaceAll('-','+').replaceAll('_','/')),c=>c.charCodeAt(0))}
export async function hash(token){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(token))),b=>b.toString(16).padStart(2,'0')).join('')}
async function unlock(token,cap,payload){
 const wrappingKey=await crypto.subtle.importKey('raw',bytes(token),'AES-GCM',false,['decrypt']);
 const rawKey=await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes(cap.iv)},wrappingKey,bytes(cap.wrapped));
 const contentKey=await crypto.subtle.importKey('raw',rawKey,'AES-GCM',false,['decrypt']);
 const compressed=await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes(payload.iv)},contentKey,bytes(payload.cipher));
 return new Response(new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
}
export function createHandler(payload,landing){return {async fetch(request,env){
 const url=new URL(request.url);
 if(url.pathname==='/health'&&['GET','HEAD'].includes(request.method))return json({ok:true,service:'vm-private-preview',version:1});
 if(url.pathname==='/robots.txt')return new Response('User-agent: *\nDisallow: /\n',{headers:{...HEADERS,'content-type':'text/plain'}});
 if(url.pathname==='/'&&['GET','HEAD'].includes(request.method))return new Response(request.method==='HEAD'?null:landing,{headers:{...HEADERS,'content-type':'text/html; charset=utf-8','content-security-policy':"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:; connect-src 'self'; frame-src 'self' blob:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"}});
 if(!['/open','/status'].includes(url.pathname))return json({error:'not_found'},404);
 if(request.method!=='POST')return json({error:'method_not_allowed'},405);
 if(request.headers.get('origin')!==url.origin)return json({error:'origin_rejected'},403);
 if(!request.headers.get('content-type')?.startsWith('application/json'))return json({error:'invalid_content_type'},415);
 const body=await request.text();if(body.length>256)return json({error:'request_too_large'},413);
 let token;try{token=JSON.parse(body).token}catch{return json({error:'invalid_json'},400)}
 if(typeof token!=='string'||!/^[A-Za-z0-9_-]{43}$/.test(token))return json({error:'invalid_link'},403);
 const id=await hash(token),cap=payload.caps[id];if(!cap)return json({error:'invalid_link'},403);
 const stub=env.PREVIEWS.get(env.PREVIEWS.idFromName(id));
 const response=await stub.fetch(new Request('https://state.local/',{method:'POST',body:JSON.stringify({operation:url.pathname==='/open'?'open':'status',ttl:cap.ttl})}));
 const state=await response.json();if(!response.ok)return json(state,response.status);
 if(url.pathname==='/status')return json(state);
 try{return json({...state,html:await unlock(token,cap,payload)})}catch{return json({error:'preview_unavailable'},500)}
}}}
