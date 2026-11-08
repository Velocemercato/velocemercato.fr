import { strict as assert } from 'node:assert';
import { pbkdf2Sync } from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';
import { StudioStorage } from './worker.mjs';

const origin='https://atelier.test', db=new DatabaseSync(':memory:');
const sql={exec(statement,...parameters) {
  if (statement.trim().startsWith('CREATE TABLE')) {
    db.exec(statement);
    return {toArray:()=>[]};
  }
  const rows=db.prepare(statement).all(...parameters);
  return {toArray:()=>rows};
}};
const testPassword='Test-atelier-random-secret-2026';
const salt='00000000000000000000000000000001';
const env={STUDIO_BOOTSTRAP:salt+':'+pbkdf2Sync(testPassword,salt,100000,32,'sha256').toString('hex'),
  ASSETS:{fetch:()=>new Response('<h1>Atelier protégé</h1>')}};
const app=new StudioStorage({storage:{sql}},env);
const req=(path,{method='GET', body, session, from=origin}={})=>app.fetch(new Request(origin+path,{
  method,body,headers:{origin:from,'cf-connecting-ip':'192.0.2.13',...(session?{cookie:session}:{})}}));
const post=(path,body,session)=>req(path,{method:'POST',body:JSON.stringify(body),session});
const codePost=(path,value)=>req(path,{method:'POST',body:new URLSearchParams({code:value})});
const privatePreview='/p/';
assert.equal((await req('/')).status,200);
assert.equal((await req('/atelier')).status,303);
assert.equal((await req('/app.html')).status,404);
assert.equal((await req('/api/projects')).status,401);
assert.equal((await codePost('/session','mauvais')).status,403);
const login=await codePost('/session',testPassword);
assert.equal(login.status,303);
const cookie=login.headers.get('set-cookie').split(';')[0];
assert.equal((await req('/atelier',{session:cookie})).status,200);
assert.equal((await req('/api/projects',{method:'POST',body:'{}',session:cookie,from:'https://evil.test'})).status,403);
const photo='data:image/jpeg;base64,/9j/AA==';
const saved=await (await post('/api/projects',{data:{kind:'paiement',name:'Salon VM fictif',title:'<script>test</script>',description:'Privé',photo,payment:'javascript:alert(1)'}},cookie)).json();
assert.match(saved.code,/^[0-9A-F]{16}$/);
const path=privatePreview+saved.id;
const gate=await req(path);
assert.equal(gate.headers.get('cache-control'),'no-store');
assert.doesNotMatch(await gate.text(),/Salon VM|Privé|base64/);
assert.equal((await codePost(path,'incorrect')).status,403);
const open=await codePost(path,saved.code);
assert.equal(open.status,200);
const html=await open.text();
assert.match(html,/&lt;script&gt;test&lt;\/script&gt;/);
assert.match(html,/base64/);
assert.doesNotMatch(html,/javascript:/);
const changes=await Promise.all([post('/api/projects/'+saved.id,{revision:1,data:{name:'Projet 2'}},cookie),
  post('/api/projects/'+saved.id,{revision:1,data:{name:'Projet 3'}},cookie)]);
assert.deepEqual(changes.map(r=>r.status).sort(),[200,409]);
const rotated=await (await post('/api/projects/'+saved.id+'/rotate',{revision:2},cookie)).json();
assert.equal((await codePost(path,saved.code)).status,403);
assert.equal((await codePost(path,rotated.code)).status,200);
assert.equal((await post('/api/projects/'+saved.id+'/close',{revision:3},cookie)).status,200);
assert.equal((await codePost(path,rotated.code)).status,403);
const newPassword='Un autre code long unique-2026';
assert.equal((await post('/api/password',{current:testPassword,password:newPassword},cookie)).status,200);
assert.equal((await req('/api/projects',{session:cookie})).status,401);
assert.equal((await codePost('/session',testPassword)).status,403);
assert.equal((await codePost('/session',newPassword)).status,303);
if(process.env.TEST_QR==='1') {
  const login=await codePost('/session',newPassword);
  const session=login.headers.get('set-cookie').split(';')[0];
  const qr=await (await post('/api/projects',{data:{kind:'qr',name:'QR VM',qrUrl:'https://vmunivers.fr/'}},session)).json();
  const svg=await (await codePost('/p/'+qr.id,qr.code)).text();
  assert.match(svg,/<svg[\s\S]*<path/);
}
console.log('ATELIER OK · accès, isolation, photo, édition concurrente, rotation et révocation.');
