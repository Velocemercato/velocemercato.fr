import assert from 'node:assert/strict';import {registerHooks} from 'node:module';import {DatabaseSync} from 'node:sqlite';import test from 'node:test';
registerHooks({resolve(s,c,n){if(s==='cloudflare:workers')return {url:'data:text/javascript,export class DurableObject {constructor(ctx,env){this.ctx=ctx;this.env=env}}',shortCircuit:true};return n(s,c)}});
const {default:worker,Store}=await import('../src/index.js');
test('Creator intégré : origine, jeton, cookie, navigation multipage et refus des exports',async()=>{
 const db=new DatabaseSync(':memory:'),env={ADMIN_TOKEN:'local-only'};
 const store=new Store({storage:{sql:{exec(sql,...args){if(sql.trimStart().startsWith('SELECT'))return db.prepare(sql).all(...args);if(args.length)db.prepare(sql).run(...args);else db.exec(sql);return []}}}},env);
 env.STORE={idFromName:x=>x,get:()=>({fetch:(u,i)=>store.fetch(new Request(u,i))})};
 const origin='https://atelier.velocemercato.fr';
 const post=(action,body,token='',from=origin)=>worker.fetch(new Request(origin+'/creator/api/'+action,{method:'POST',headers:{origin:from,'content-type':'application/json',authorization:'Bearer '+token},body:JSON.stringify(body)}),env);
 const brief={name:'Recette VM',sector:'commerce',email:'test@example.invalid'};
 assert.equal((await post('create',brief,'','https://evil.invalid')).status,403);
 const r=await post('create',brief);assert.equal(r.status,201);const cookie=r.headers.get('set-cookie').split(';')[0],p=await r.json();assert.ok(p.token);
 const get=path=>worker.fetch(new Request(origin+path,{headers:{cookie}}),env),base='/creator/preview/'+p.id+'/';
 for(const page of ['index.html','contact.html','style.css']){const r=await get(base+page);assert.equal(r.status,200);assert.match(r.headers.get('content-type'),page.endsWith('css')?/text\/css/:/text\/html/)}
 assert.equal((await worker.fetch(new Request(origin+base+'index.html'),env)).status,404);
 assert.equal((await post('get',{id:p.id},'wrong-token')).status,404);
 assert.equal((await post('list',{admin:true},p.token)).status,403);
 for(const action of ['publish','export','payment'])assert.equal((await post(action,{id:p.id,admin:true},p.token)).status,403);
 const edit=await post('edit',{id:p.id,text:'couleur rouge'},p.token);assert.equal(edit.status,200);assert.equal((await edit.json()).version,2);
 assert.match(await (await get(base+'index.html')).text(),/Recette VM/);db.close();
});
