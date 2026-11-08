const sections = {
  site:['Site vitrine','Découvrir','Présentation\nOffres et services\nContact et horaires'],
  paiement:['Site avec paiement','Commander','Catalogue\nCommande\nLien de paiement'],
  application:['Application','Ouvrir l’application','Accueil\nFonctionnalités\nCompte ou contact'],
  encart:['Encart publicitaire','Découvrir l’offre','Visuel publicitaire\nAccroche et offre\nEmplacement média'],
  carte:['Carte de visite','Nous contacter','Nom et métier\nCoordonnées\nQR ou adresse web'],
  qr:['Support QR','Scanner le QR','Destination du QR\nAccroche\nSupport de diffusion'],
  vetement:['Vêtement','Voir la collection','Emplacement du logo\nCouleurs et tailles\nQuantité souhaitée'],
  goodie:['Accessoire ou goodie','Découvrir','Matière et dimensions\nPersonnalisation\nQuantité souhaitée'],
  reseaux:['Kit réseaux automatisé','Voir le kit','Textes à copier\nVisuels à partager\nPlanning de publication'],
};
const trades = [
  ['Coiffure','Une nouvelle coupe, une nouvelle énergie.','Coupes et coiffages\nCouleur et soins\nRendez-vous'],
  ['Barbier','Un style précis, jusque dans les détails.','Coupe\nTaille de barbe\nForfaits'],
  ['Restaurant','À table, on s’occupe du reste.','La carte\nRéserver une table\nÀ emporter'],
  ['Boulangerie','Du bon pain, chaque jour.','Pains et viennoiseries\nPâtisseries\nCommandes'],
  ['Artisan','Un savoir-faire de proximité.','Réalisations\nPrestations\nDevis'],
  ['Garage','Le bon entretien, au bon moment.','Entretien\nRéparation\nRendez-vous atelier'],
  ['Club sportif','Rejoins l’équipe.','Équipes et horaires\nInscriptions\nPartenaires'],
  ['Commerçant','Les bonnes trouvailles, près de chez vous.','Produits\nNouveautés\nHoraires'],
  ['Bien-être','Un moment pour soi.','Séances\nForfaits\nRendez-vous'],
  ['Photographe','Les instants qui restent.','Portfolio\nSéances\nRéservation'],
  ['Association','Ensemble, on fait avancer le projet.','Notre mission\nÉvénements\nAdhésion'],
  ['Événement','Un rendez-vous à ne pas manquer.','Programme\nInfos pratiques\nRéservations'],
];
const themes = {net:'Graphique', chaleur:'Chaleureux', premium:'Premium'};
const byId = id => document.getElementById(id);
const form = byId('editor');
let kind = 'site', theme = 'net', model = '', photo = '', current = null;
let locked = false;
const api = async (path, data) => {
  const reply = await fetch('/api/'+path,data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  if (reply.status===401) location.assign('/');
  const result = await reply.json();
  if (!reply.ok) throw new Error(result.error||'Action indisponible.');
  return result;
};
const button = (label, action, classes='ghost') => {
  const b=document.createElement('button');
  b.type='button'; b.className=classes; b.textContent=label; b.onclick=action;
  return b;
};
const note = message => {byId('notice').textContent=message;};
const category = () => {
  byId('categories').replaceChildren(...Object.entries(sections).map(([key,[title]])=>{
    const b=button(title,()=>{kind=key;model='';category();catalog();render();});
    b.setAttribute('aria-pressed',String(key===kind));
    return b;
  }));
};
const normalized = value => value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
function catalog() {
  const query=normalized(byId('search').value.trim());
  const buttons=[];
  for(const trade of trades) for(const [design,label] of Object.entries(themes)) {
    const title=trade[0]+' · '+label;
    if (query && !normalized(title).includes(query)) continue;
    const b=button(trade[0],()=>{
      theme=design;model=title;
      form.elements.title.value=trade[1];
      form.elements.description.value=kind==='site'?trade[1]+' Découvrez les services et les informations pratiques.':
        sections[kind][0]+' pour '+trade[0].toLowerCase()+'. Adaptez cette proposition à votre identité et à votre offre.';
      form.elements.services.value=kind==='site'?trade[2]:sections[kind][2];
      form.elements.cta.value=sections[kind][1];
      render();catalog();
    },'model');
    const hint=document.createElement('small');hint.textContent=label;b.append(hint);
    b.setAttribute('aria-pressed',String(model===title));buttons.push(b);
  }
  byId('models').replaceChildren(...buttons);
  byId('model-count').textContent=buttons.length+' modèle'+(buttons.length===1?'':'s')+' · '+sections[kind][0];
}
function data() {
  return {...Object.fromEntries(new FormData(form)),kind,theme,template:model,photo};
}
function render() {
  const d=data();
  byId('p-kind').textContent=sections[kind][0]+' · '+themes[theme];
  byId('p-title').textContent=d.title||d.name||'Titre du projet';
  byId('p-desc').textContent=d.description||'Ta présentation apparaîtra ici.';
  byId('p-cta').textContent=d.cta||sections[kind][1];
  byId('p-services').replaceChildren(...String(d.services||'').split('\n').filter(Boolean).slice(0,8).map(value=>{
    const li=document.createElement('li');li.textContent=value;return li;
  }));
  const image=byId('p-photo');image.hidden=!photo;
  if(photo) image.src=photo; else image.removeAttribute('src');
  byId('preview').className='mini '+theme;
  byId('paymentRow').hidden=kind!=='paiement';
  byId('qrRow').hidden=kind!=='qr';
}
function updateShare(result) {
  const previous=current?.code||'';
  current={...result,code:result.code||(result.active?previous:'')};
  byId('share').hidden=false;
  byId('share-url').value=result.url;
  byId('share-code').value=current.code;
  byId('copy-code').disabled=!current.code;
  byId('open-preview').href=result.url;
  byId('close').disabled=!result.active;
  byId('share-status').textContent=result.active?'Accès client actif. Envoie le code séparément du lien.':'Accès coupé. Un nouveau code réactivera le lien.';
  byId('save').textContent='Enregistrer les changements';
}
async function projects() {
  const rows=await api('projects');
  const box=byId('projects');
  box.replaceChildren(...rows.map(row=>{
    const b=button(row.name,()=>act(()=>openProject(row.id)),'ghost project-link');
    const label=document.createElement('small'); label.textContent=row.active?'Actif':'Fermé';b.append(label);
    return b;
  }));
  if(!rows.length) box.textContent='Aucun projet enregistré.';
}
async function openProject(id) {
  const r=await api('projects/'+id);
  current=null;
  form.reset();
  for(const [field,value] of Object.entries(r.data)) {
    if(form.elements[field]) form.elements[field].value=value;
  }
  kind=r.data.kind; theme=r.data.theme; model=r.data.template; photo=r.data.photo;
  updateShare({id,url:location.origin+'/p/'+id,revision:r.revision,active:r.active,code:''});
  category();catalog();render();note('Projet ouvert.');
  form.scrollIntoView({block:'start'});
}
async function act(action) {
  if(locked)return;
  locked=true;
  try{await action();}catch(error){note(error.message);}
  finally{locked=false;}
}
form.onsubmit=event=>{
  event.preventDefault();
  act(async()=>{
    const result=await api('projects'+(current?'/'+current.id:''),{data:data(),revision:current?.revision});
    updateShare(result);note('Projet enregistré.');await projects();
  });
};
byId('rotate').onclick=()=>act(async()=>{
  if(!confirm('Générer un nouveau code ? L’ancien cessera de fonctionner.'))return;
  updateShare(await api('projects/'+current.id+'/rotate',{revision:current.revision}));
  note('Nouveau code prêt à copier.');await projects();
});
byId('close').onclick=()=>act(async()=>{
  if(!confirm('Couper l’accès de ce lien ?'))return;
  updateShare(await api('projects/'+current.id+'/close',{revision:current.revision}));
  note('Le lien est maintenant fermé.');await projects();
});
for(const key of ['link','code']) byId('copy-'+key).onclick=()=>act(async()=>{
  await navigator.clipboard.writeText(byId(key==='link'?'share-url':'share-code').value);note(key==='link'?'Lien copié.':'Code copié.');
});
byId('new').onclick=()=>{if(current&&!confirm('Ouvrir un nouveau projet ?'))return;current=null;form.reset();photo='';model='';
  byId('share').hidden=true;byId('share-status').textContent='Le lien et le code apparaîtront ici après l’enregistrement.';
  byId('save').textContent='Créer le lien client';render();catalog();note('');};
byId('remove-photo').onclick=()=>{photo='';byId('photo').value='';render();};
byId('photo').onchange=()=>act(async()=>{
  const file=byId('photo').files[0];
  if(!file)return;
  if(!/^image\/(jpeg|png|webp)$/.test(file.type)||file.size>18*1024*1024)throw new Error('Choisis une photo JPG, PNG ou WebP de moins de 18 Mo.');
  const image=await createImageBitmap(file);
  const ratio=Math.min(1,1300/Math.max(image.width,image.height));
  const canvas=document.createElement('canvas');canvas.width=Math.round(image.width*ratio);canvas.height=Math.round(image.height*ratio);
  const context=canvas.getContext('2d');context.fillStyle='#fff';context.fillRect(0,0,canvas.width,canvas.height);
  context.drawImage(image,0,0,canvas.width,canvas.height);image.close();
  let quality=.84;
  let result=canvas.toDataURL('image/jpeg',quality);
  while(result.length>720000&&quality>.30){quality-=.10;result=canvas.toDataURL('image/jpeg',quality);}
  if(result.length>720000)throw new Error('Cette photo reste trop lourde après compression.');
  photo=result;render();note('Photo prête à enregistrer.');
});
byId('search').oninput=catalog;
form.oninput=render;
byId('logout').onclick=()=>act(async()=>{await api('logout');location.assign('/');});
byId('passwordOpen').onclick=()=>{byId('passwordForm').reset();byId('passwordNotice').textContent='';byId('passwordDialog').showModal();};
byId('passwordClose').onclick=()=>byId('passwordDialog').close();
byId('passwordForm').onsubmit=async event=>{
  event.preventDefault();
  try{await api('password',Object.fromEntries(new FormData(event.target)));location.assign('/');}
  catch(error){byId('passwordNotice').textContent=error.message;}
};
category();catalog();render();act(projects);
