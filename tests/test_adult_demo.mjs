import test from 'node:test';
import assert from 'node:assert/strict';
import {profiles,visibleProfiles,freshState,setNickname,addMessage,messagesFor,blockProfile,unblockProfile,addReport} from '../prototypes/communaute-adulte/model.mjs';
test('meeting preferences and moments combine with city and profile filters',()=>{
  const state=freshState();
  assert.deepEqual(visibleProfiles(state,'couple','besancon','recoit','vacances').map(p=>p.id),['p4']);
  assert.deepEqual(visibleProfiles(state,'femme','paris','hotel','weekend').map(p=>p.id),['p2']);
  assert.deepEqual(visibleProfiles(state,'tous','musique','hotel','vacances').map(p=>p.id),['p1','p5']);
  assert.equal(visibleProfiles(state,'femme','','recoit').length,0);
});
test('blocking hides profile and stops new private messages, unblocking restores access',()=>{
  const state=freshState();addMessage(state,{target:'p1',text:'Message de test'});
  blockProfile(state,'p1');
  assert.equal(visibleProfiles(state).some(p=>p.id==='p1'),false);
  assert.throws(()=>addMessage(state,{target:'p1',text:'Un autre message'}),/bloqué/);
  assert.equal(messagesFor(state,'p1').length,1);
  unblockProfile(state,'p1');
  assert.equal(visibleProfiles(state).length,profiles.length);
  assert.doesNotThrow(()=>addMessage(state,{target:'p1',text:'Après déblocage'}));
});
test('rooms and private conversations keep their messages separate',()=>{
  const state=freshState();setNickname(state,'Pseudo fictif');
  addMessage(state,{target:'general',text:'Salon',now:new Date('2026-10-23T18:00:00Z')});
  addMessage(state,{target:'presentations',text:'Présentation'});
  addMessage(state,{target:'p2',text:'Privé'});
  assert.deepEqual(messagesFor(state,'general').map(m=>m.text),['Salon']);
  assert.deepEqual(messagesFor(state,'p2').map(m=>m.text),['Privé']);
  assert.equal(messagesFor(state,'p1').length,0);
  assert.equal(state.messages[0].author,'Pseudo fictif');
  assert.equal(state.messages[0].time,'2026-10-23T18:00:00.000Z');
});
test('empty or oversized text and unknown targets cannot create messages',()=>{
  const state=freshState();
  for(const text of ['  ','a'.repeat(1001)])assert.throws(()=>addMessage(state,{target:'general',text}));
  for(const target of ['missing','constructor','__proto__'])assert.throws(()=>addMessage(state,{target,text:'Test'}),/introuvable/);
  assert.equal(state.messages.length,0);
});
test('reports require a known profile and reason and remain separate from messages',()=>{
  const state=freshState();
  addReport(state,{profileId:'p1',reason:'age',detail:'Exemple fictif'});
  assert.equal(state.reports[0].detail,'Exemple fictif');
  assert.equal(state.messages.length,0);
  assert.throws(()=>addReport(state,{profileId:'missing',reason:'autre'}),/introuvable/);
  assert.throws(()=>addReport(state,{profileId:'p1',reason:'constructor'}),/motif/);
  assert.throws(()=>addReport(state,{profileId:'p1',reason:'autre',detail:'a'.repeat(501)}),/500/);
});
test('a fresh session has no nickname, message, block or report from the previous session',()=>{
  const old=freshState();setNickname(old,'Ancien pseudo');blockProfile(old,'p1');addReport(old,{profileId:'p1',reason:'autre'});addMessage(old,{target:'general',text:'Ancien message'});
  const next=freshState();assert.equal(next.nickname,'Visiteur démo');assert.equal(next.messages.length,0);assert.equal(next.reports.length,0);assert.equal(next.blocked.size,0);assert.equal(next.nextId,1);
});
test('message and nickname text are preserved as text without generating automated replies',()=>{
  const state=freshState();setNickname(state,'<img src=x onerror=alert(1)>');
  addMessage(state,{target:'p1',text:'<script>alert(1)</script>'});
  assert.equal(state.messages.length,1);assert.equal(state.messages[0].text,'<script>alert(1)</script>');
  assert.equal(state.messages[0].author,'<img src=x onerror=alert(1)>');
});
