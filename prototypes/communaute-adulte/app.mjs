import {profiles,rooms,reportReasons,meetingLabels,availabilityLabels,freshState,visibleProfiles,findProfile,setNickname,addMessage,messagesFor,blockProfile,unblockProfile,addReport} from './model.mjs';
const $=id=>document.getElementById(id);
let state=freshState(), currentRoom='general', currentProfile='p1', reportTarget=null, toastTimer;
const views=['rencontres','salon','messages','charte'];
function el(tag,attrs={},...children){
  const node=document.createElement(tag);
  for(const [key,value] of Object.entries(attrs)){
    if(typeof value==='function'&&key.startsWith('on')) node.addEventListener(key.slice(2),value);
    else if(key==='class') node.className=value;
    else node.setAttribute(key,String(value));
  }
  for(const child of children.flat()) if(child!==null&&child!==undefined) node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  return node;
}
function toast(text){clearTimeout(toastTimer);$('toast').textContent=text;$('toast').hidden=false;toastTimer=setTimeout(()=>$('toast').hidden=true,6000);}
function portrait(profile,detail=false){return el('div',{class:`portrait${detail?' detail-portrait':''}`,'data-tone':profile.tone,'aria-hidden':'true'},el('span',{class:'demo-label'},'PROFIL FICTIF'),el('span',{class:'initials'},profile.initials));}
function tagList(values){return el('div',{class:'tags'},values.map(value=>el('span',{class:'tag'},value)));}
function preferences(profile){return [...profile.meeting.map(key=>meetingLabels[key]),...profile.availability.map(key=>availabilityLabels[key])];}
function renderProfiles(){
  const list=visibleProfiles(state,$('kind').value,$('city').value,$('meeting').value,$('availability').value);
  $('profiles').replaceChildren(...list.map(profile=>el('article',{class:'profile-card'},portrait(profile),el('div',{class:'card-content'},el('h3',{class:'profile-title'},profile.name),el('p',{class:'profile-location'},`${profile.age} · ${profile.city} · ${profile.label}`),tagList(profile.tags),el('p',{class:'card-bio'},profile.bio),tagList(preferences(profile)),el('button',{type:'button',class:'card-open',onclick:()=>showProfile(profile.id),'aria-label':`Découvrir le profil fictif de ${profile.name}`},'Découvrir le profil ↗')))));
  $('result-count').textContent=`${list.length} profil${list.length>1?'s':''} fictif${list.length>1?'s':''} · Aucun membre réel dans cette démo`;
  $('empty-profiles').hidden=list.length!==0;
}
function showProfile(id){
  const profile=findProfile(id);if(!profile)return;
  const blocked=state.blocked.has(id);
  const primary=el('button',{type:'button',class:'button primary',onclick:()=>{
    $('profile-dialog').close();currentProfile=id;$('private-text').value='';renderPrivate();location.hash='messages';
  }},'Essayer un message ↗');
  primary.disabled=blocked;
  $('profile-detail').replaceChildren(portrait(profile,true),el('p',{class:'eyebrow'},'PROFIL FICTIF · DÉMONSTRATION'),el('h2',{id:'profile-title'},profile.name),el('p',{class:'detail-info'},`${profile.age} · ${profile.city} · ${profile.label}`),tagList(profile.tags),el('p',{},profile.detail),el('p',{class:'eyebrow'},'LE CADRE & LE MOMENT'),tagList(preferences(profile)),el('p',{class:'dialog-note'},'Ces préférences sont fictives. Aucune adresse précise n’est affichée. Une préférence ne vaut pas consentement à une rencontre.'),el('div',{class:'detail-actions'},primary),el('div',{class:'detail-secondary'},el('button',{type:'button',class:'text-button',onclick:()=>{
    if(blocked)unblockProfile(state,id);else blockProfile(state,id);
    $('profile-dialog').close();renderAll();toast(blocked?'Profil débloqué dans la démo.':'Profil bloqué dans la démo. Tu peux le débloquer dans Respect & sécurité.');
  }},blocked?'Débloquer ce profil':'Bloquer ce profil'),el('button',{type:'button',class:'text-button',onclick:()=>{
    $('profile-dialog').close();reportTarget=id;$('report-form').reset();$('report-target').textContent=`Profil fictif : ${profile.name}`;$('report-dialog').showModal();
  }},'Signaler · test local')));
  $('profile-dialog').showModal();
}
function fillMessages(container,target,placeholder){
  const messages=messagesFor(state,target);
  container.replaceChildren(...(messages.length ? messages.map(message=>el('article',{class:'message'},el('b',{},message.author),el('p',{},message.text),el('small',{},`${new Intl.DateTimeFormat('fr-FR',{hour:'2-digit',minute:'2-digit'}).format(new Date(message.time))} · test local, non transmis`))) : [el('p',{class:'system-message'},placeholder)]));
  container.scrollTop=container.scrollHeight;
}
function renderRoom(){
  $('room-name').textContent=rooms[currentRoom];
  document.querySelectorAll('[data-room]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.room===currentRoom)));
  fillMessages($('room-messages'),currentRoom,'Ce salon est un espace de test vide. Ajoute un premier message pour découvrir le parcours ; aucun autre membre n’est présent et aucune réponse automatique n’est générée.');
}
function renderPrivate(){
  $('threads').replaceChildren(...profiles.map(profile=>el('button',{type:'button',class:'thread-button','aria-pressed':String(profile.id===currentProfile),onclick:()=>{currentProfile=profile.id;$('private-text').value='';renderPrivate();}},el('span',{class:'mini-avatar','aria-hidden':'true'},profile.initials),el('span',{},el('b',{},profile.name),el('small',{},state.blocked.has(profile.id)?'Profil bloqué':'Profil fictif · démo')))));
  const profile=findProfile(currentProfile);const blocked=profile&&state.blocked.has(profile.id);
  $('thread-name').textContent=profile?profile.name:'Choisis un profil';
  $('thread-description').textContent=profile?`${profile.city} · profil fictif${blocked?' · bloqué':''}`:'Conversation de démonstration';
  $('thread-profile').hidden=!profile;
  $('private-text').disabled=!profile||blocked;$('private-send').disabled=!profile||blocked;
  $('private-note').textContent=blocked?'Ce profil est bloqué. Débloque-le dans Respect & sécurité pour reprendre le test.':'Message local uniquement, jamais transmis. Il disparaît au rechargement.';
  fillMessages($('private-messages'),currentProfile,'Aucune conversation réelle ici. Essaie un premier message : il restera dans cette page, sans destinataire et sans réponse simulée.');
}
function renderSafety(){
  const blocked=profiles.filter(profile=>state.blocked.has(profile.id));
  $('blocked-list').replaceChildren(...(blocked.length?blocked.map(profile=>el('div',{class:'settings-row'},el('span',{},profile.name),el('button',{type:'button',class:'text-button',onclick:()=>{unblockProfile(state,profile.id);renderAll();toast('Profil débloqué dans la démo.');}},'Débloquer'))):[el('p',{},'Aucun profil bloqué dans cette session.')]));
  $('report-list').replaceChildren(...(state.reports.length?state.reports.map(report=>el('div',{class:'settings-row'},el('div',{},el('b',{},findProfile(report.profileId).name),el('p',{},reportReasons[report.reason]),report.detail?el('p',{},report.detail):null),el('span',{class:'small-pill'},'NON TRANSMIS'))):[el('p',{},'Aucun signalement de test.')]));
}
function renderAll(){renderProfiles();renderRoom();renderPrivate();renderSafety();$('my-name').textContent=state.nickname;$('my-avatar').textContent=[...state.nickname][0].toUpperCase();}
function showView(focus=false){
  const hash=location.hash.slice(1);const view=views.includes(hash)?hash:'rencontres';
  for(const name of views)$(`view-${name}`).hidden=name!==view;
  document.querySelectorAll('[data-view]').forEach(link=>{if(link.dataset.view===view)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');});
  if(view==='salon')renderRoom();if(view==='messages')renderPrivate();
  if(focus){const title=$(`view-${view}`).querySelector('h1');title.setAttribute('tabindex','-1');title.focus({preventScroll:true});window.scrollTo({top:0,behavior:'instant'});}
}
$('filters').addEventListener('submit',event=>event.preventDefault());
for(const id of ['kind','meeting','availability'])$(id).addEventListener('change',renderProfiles);
$('city').addEventListener('input',renderProfiles);
$('filters').addEventListener('reset',()=>{queueMicrotask(renderProfiles);});
document.querySelectorAll('[data-room]').forEach(button=>button.addEventListener('click',()=>{currentRoom=button.dataset.room;$('room-text').value='';renderRoom();}));
function submitMessage(event,field,target,render){
  event.preventDefault();try{addMessage(state,{target,text:field.value});field.value='';field.setCustomValidity('');render();field.focus();}catch(error){field.setCustomValidity(error.message);field.reportValidity();}
}
$('room-form').addEventListener('submit',event=>submitMessage(event,$('room-text'),currentRoom,renderRoom));
$('private-form').addEventListener('submit',event=>submitMessage(event,$('private-text'),currentProfile,renderPrivate));
for(const id of ['room-text','private-text','nickname'])$(id).addEventListener('input',()=>$(id).setCustomValidity(''));
$('thread-profile').addEventListener('click',()=>showProfile(currentProfile));
document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',()=>$(button.dataset.close).close()));
$('report-form').addEventListener('submit',event=>{event.preventDefault();try{addReport(state,{profileId:reportTarget,reason:$('report-reason').value,detail:$('report-detail').value});$('report-dialog').close();renderSafety();toast('Signalement de test enregistré dans la page. Aucun envoi à un modérateur.');}catch(error){toast(error.message);}});
$('edit-profile').addEventListener('click',()=>{$('nickname').value=state.nickname;$('my-profile-dialog').showModal();});
$('my-profile-form').addEventListener('submit',event=>{event.preventDefault();try{setNickname(state,$('nickname').value);$('my-profile-dialog').close();renderAll();toast('Pseudo de test mis à jour. Aucun compte créé.');}catch(error){$('nickname').setCustomValidity(error.message);$('nickname').reportValidity();}});
$('reset-demo').addEventListener('click',()=>{
  state=freshState();currentRoom='general';currentProfile='p1';reportTarget=null;
  for(const id of ['filters','room-form','private-form','report-form','my-profile-form'])$(id).reset();
  for(const id of ['room-text','private-text','nickname'])$(id).setCustomValidity('');
  renderAll();toast('La démo a été réinitialisée. Toutes les données de test ont été effacées.');
});
window.addEventListener('hashchange',()=>showView(true));
$('entry-dialog').addEventListener('cancel',event=>event.preventDefault());
$('entry-form').addEventListener('submit',event=>{event.preventDefault();if($('adult-check').checked)$('entry-dialog').close();});
renderAll();showView();$('entry-dialog').showModal();
