import test from 'node:test';
import assert from 'node:assert/strict';
import {mapsSearch,categoryOrDefault} from '../services/search.mjs';
test('all three categories open the intended professional search', () => {
  for (const [key,words] of [['cbd','boutique CBD'],['caviste','caviste magasin alcool'],['taxi','taxi VTC']]) {
    const url = new URL(mapsSearch(key,'  Belfort  '));
    assert.equal(url.origin,'https://www.google.com');
    assert.equal(url.pathname,'/maps/search/');
    assert.equal(url.searchParams.get('api'),'1');
    assert.equal(url.searchParams.get('query'),`${words} Belfort`);
  }
});
test('open-now request does not imply taxi availability', () => {
  assert.match(new URL(mapsSearch('caviste','90000',true)).searchParams.get('query'),/ouvert maintenant$/);
  assert.doesNotMatch(new URL(mapsSearch('taxi','90000',true)).searchParams.get('query'),/ouvert/);
});
test('untrusted city remains a single encoded query value', () => {
  const city='Évry & api=0#<script>alert(1)</script>';
  const url = new URL(mapsSearch('cbd',city));
  assert.equal(url.searchParams.get('query'),`boutique CBD ${city}`);
  assert.equal(url.searchParams.get('api'),'1');
  assert.equal(url.hash,'');
  assert.equal([...url.searchParams].length,2);
});
test('invalid categories cannot select object prototype properties', () => {
  for (const value of ['__proto__','constructor','toString',null,'unknown']) assert.equal(categoryOrDefault(value),'cbd');
});
test('blank locations are rejected and input length is bounded', () => {
  assert.throws(() => mapsSearch('cbd','  '),/ville/);
  assert.equal(new URL(mapsSearch('cbd','a'.repeat(150))).searchParams.get('query'),'boutique CBD '+'a'.repeat(100));
});
