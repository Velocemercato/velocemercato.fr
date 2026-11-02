import test from 'node:test';
import assert from 'node:assert/strict';
import {mapsSearch,categoryOrDefault,categories} from '../services/search.mjs';
test('each category searches the correct professional near the chosen city',()=>{
 for(const [key,words] of Object.entries(categories)){
  const url=new URL(mapsSearch(key,' Belfort '));
  assert.equal(url.origin,'https://www.google.com');
  assert.equal(url.pathname,'/maps/search/');
  assert.equal(url.searchParams.get('api'),'1');
  assert.equal(url.searchParams.get('query'),words+' près de Belfort');
 }
});
test('open-now does not imply taxi availability',()=>{
 assert.match(new URL(mapsSearch('garage','90000',true)).searchParams.get('query'),/ouvert maintenant$/);
 assert.doesNotMatch(new URL(mapsSearch('taxi','90000',true)).searchParams.get('query'),/ouvert/);
});
test('untrusted city is URL-encoded as one query',()=>{
 const city='Évry & api=0#<script>alert(1)</script>';
 const url=new URL(mapsSearch('garage',city));
 assert.equal(url.searchParams.get('query'),'garage automobile près de '+city);
 assert.equal(url.searchParams.get('api'),'1');
 assert.equal(url.hash,'');
 assert.equal([...url.searchParams].length,2);
});
test('invalid category falls back safely',()=>{
 for(const x of ['__proto__','constructor','toString',null,'unknown'])assert.equal(categoryOrDefault(x),'garage');
});
test('blank city is rejected and input is bounded',()=>{
 assert.throws(()=>mapsSearch('garage',' '),/ville/);
 assert.equal(new URL(mapsSearch('garage','a'.repeat(150))).searchParams.get('query'),'garage automobile près de '+'a'.repeat(100));
});
