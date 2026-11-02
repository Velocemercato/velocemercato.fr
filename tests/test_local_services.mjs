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
import {readFileSync} from 'node:fs';
test('every /pro/ shortcut opens its own category, never the default',()=>{
 const pro=readFileSync(new URL('../pro/index.html',import.meta.url),'utf8');
 const keys=[...pro.matchAll(/\/services\/\?categorie=([a-z]+)/g)].map(m=>m[1]);
 assert.ok(keys.length>=3);
 for(const k of keys) assert.equal(categoryOrDefault(k),k);
});
test('the page offers every category and no fake travel-time filter',()=>{
 const page=readFileSync(new URL('../services/index.html',import.meta.url),'utf8');
 for(const k of Object.keys(categories)){
  assert.match(page,new RegExp(`data-category="${k}"`));
  assert.match(page,new RegExp(`<option value="${k}"`));
 }
 assert.doesNotMatch(page,/id="distance"/);
 assert.match(page,/modération/);
});
test('mapsSearch ignores any extra argument',()=>{
 assert.equal(mapsSearch('cbd','Belfort',false,40),mapsSearch('cbd','Belfort'));
 assert.equal(new URL(mapsSearch('caviste','Vesoul')).searchParams.get('query'),'caviste magasin alcool près de Vesoul');
});
