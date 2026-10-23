export const meetingLabels=Object.freeze({recoit:'Reçoit chez soi',deplace:'Se déplace',hotel:'Hôtel'});
export const availabilityLabels=Object.freeze({soiree:'Soirée',weekend:'Week-end',vacances:'Vacances'});
export const profiles = Object.freeze([
  {id:'p1',meeting:['recoit','hotel'],availability:['weekend','vacances'],name:'Camille & Alex',age:'32 & 35 ans',city:'Lyon',kind:'couple',label:'Couple',initials:'C+A',tone:'1',tags:['Sorties','Musique','Découverte'],bio:'Un verre, une conversation, et le plaisir de découvrir de nouvelles personnes.',detail:'Nous aimons les soirées où l’on peut discuter sans se presser. À la recherche de rencontres respectueuses, avec humour et curiosité.'},
  {id:'p2',meeting:['deplace','hotel'],availability:['soiree','weekend'],name:'Élise',age:'29 ans',city:'Paris',kind:'femme',label:'Femme',initials:'É',tone:'2',tags:['Art','Conversation','Liberté'],bio:'Curieuse, indépendante, et toujours partante pour une belle conversation.',detail:'Une exposition, une balade, puis une conversation qui dure. J’aime prendre le temps de faire connaissance et garder le choix de mon rythme.'},
  {id:'p3',meeting:['recoit','deplace'],availability:['weekend'],name:'Thomas',age:'36 ans',city:'Belfort',kind:'homme',label:'Homme',initials:'T',tone:'3',tags:['Nature','Cuisine','Échanges'],bio:'Faire connaissance simplement, avec de l’humour et sans pression.',detail:'Passionné de cuisine et de grands espaces. Ici pour discuter et rencontrer des personnes qui partagent le goût des échanges sincères.'},
  {id:'p4',meeting:['recoit','deplace','hotel'],availability:['weekend','vacances'],name:'Sarah & Julien',age:'34 & 37 ans',city:'Besançon',kind:'couple',label:'Couple',initials:'S+J',tone:'4',tags:['Danse','Sorties','Complicité'],bio:'Une complicité à deux, et l’envie de nouvelles rencontres à notre rythme.',detail:'Nous apprécions les lieux chaleureux et les échanges simples. Nous décidons ensemble de nos rencontres et respectons les limites de chacun.'},
  {id:'p5',meeting:['deplace','hotel'],availability:['vacances','weekend'],name:'Léa',age:'31 ans',city:'Dijon',kind:'femme',label:'Femme',initials:'L',tone:'5',tags:['Voyages','Musique','Respect'],bio:'De l’ouverture d’esprit, de la spontanéité et beaucoup de respect.',detail:'J’aime voyager et découvrir des concerts. Une rencontre commence pour moi par une vraie discussion, sans attente imposée.'},
  {id:'p6',meeting:['recoit','hotel'],availability:['soiree','weekend'],name:'Nicolas',age:'40 ans',city:'Strasbourg',kind:'homme',label:'Homme',initials:'N',tone:'6',tags:['Photo','Culture','Discussion'],bio:'Les meilleures rencontres commencent souvent par un simple bonjour.',detail:'Photographie, cinéma et petites découvertes du quotidien. Je privilégie la discrétion, la bienveillance et les conversations spontanées.'}
].map(profile => Object.freeze({...profile,tags:Object.freeze(profile.tags),meeting:Object.freeze(profile.meeting),availability:Object.freeze(profile.availability)})));
export const rooms = Object.freeze({general:'Le lounge',presentations:'Présentations',sorties:'Idées de sorties'});
export const reportReasons = Object.freeze({harcelement:'Harcèlement ou comportement insistant',contenu:'Contenu inapproprié ou sans consentement',age:'Doute sur la majorité',usurpation:'Faux profil ou usurpation',autre:'Autre'});
export const normalize = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
export function freshState(){return {nickname:'Visiteur démo',blocked:new Set(),reports:[],messages:[],nextId:1};}
export function findProfile(id){return profiles.find(profile => profile.id === id);}
export function visibleProfiles(state,kind='tous',query='',meeting='tous',availability='tous'){
  const needle=normalize(query.trim());
  return profiles.filter(profile => !state.blocked.has(profile.id) && (kind==='tous'||profile.kind===kind) && (meeting==='tous'||profile.meeting.includes(meeting)) && (availability==='tous'||profile.availability.includes(availability)) && normalize([profile.name,profile.city,...profile.tags].join(' ')).includes(needle));
}
export function setNickname(state,value){
  const nickname=String(value).trim();
  if(!nickname||nickname.length>30) throw new Error('Choisis un pseudo de 1 à 30 caractères.');
  state.nickname=nickname;
}
export function addMessage(state,{target,text,now=new Date()}){
  const isRoom=Object.hasOwn(rooms,target);
  const profile=findProfile(target);
  if(!isRoom&&!profile) throw new Error('Conversation introuvable.');
  if(profile&&state.blocked.has(target)) throw new Error('Ce profil est bloqué.');
  const body=String(text).trim();
  if(!body||body.length>1000) throw new Error('Écris un message de 1 à 1 000 caractères.');
  const message={id:state.nextId++,target,text:body,author:state.nickname,time:now.toISOString()};
  state.messages.push(message);
  return message;
}
export function messagesFor(state,target){return state.messages.filter(message => message.target===target);}
export function blockProfile(state,id){
  if(!findProfile(id)) throw new Error('Profil introuvable.');
  state.blocked.add(id);
}
export function unblockProfile(state,id){state.blocked.delete(id);}
export function addReport(state,{profileId,reason,detail=''}){
  if(!findProfile(profileId)) throw new Error('Profil introuvable.');
  if(!Object.hasOwn(reportReasons,reason)) throw new Error('Choisis un motif de signalement.');
  const text=String(detail).trim();
  if(text.length>500) throw new Error('Limite les précisions à 500 caractères.');
  const report={id:state.nextId++,profileId,reason,detail:text};
  state.reports.push(report);
  return report;
}
