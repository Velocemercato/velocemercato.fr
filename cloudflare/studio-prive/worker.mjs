const utf8 = new TextEncoder();
const random = (n = 24) => Array.from(crypto.getRandomValues(new Uint8Array(n)), b => b.toString(16).padStart(2, '0')).join('');
const sha = async value => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', utf8.encode(value))), b => b.toString(16).padStart(2, '0')).join('');
const passwordHash = async (password, salt) => {
  const key = await crypto.subtle.importKey('raw', utf8.encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({name:'PBKDF2', hash:'SHA-256', salt:utf8.encode(salt), iterations:100000}, key, 256);
  return Array.from(new Uint8Array(bits), b => b.toString(16).padStart(2, '0')).join('');
};
const equal = (a, b) => {
  if (a.length !== b.length) return false;
  let difference = 0;
  for (let i = 0; i < a.length; i++) difference |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return difference === 0;
};
const headers = {
  'cache-control':'no-store', 'x-robots-tag':'noindex, nofollow, noarchive',
  'referrer-policy':'no-referrer', 'x-content-type-options':'nosniff',
  'content-security-policy':"default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'",
};
const response = (body, status, type, extra = {}) => new Response(body, {status, headers:{...headers,'content-type':type,...extra}});
const json = (value, status = 200, extra) => response(JSON.stringify(value), status, 'application/json; charset=utf-8', extra);
const html = (value, status = 200) => response(value, status, 'text/html; charset=utf-8');
const redirect = location => new Response(null, {status:303, headers:{...headers, location}});
const e = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const text = (value, size) => String(value ?? '').trim().slice(0, size);
const validImage = value => typeof value === 'string' && value.length < 750000 &&
  /^data:image\/(jpeg;base64,\/9j\/|png;base64,iVBORw0KGgo)[A-Za-z0-9+/]*={0,2}$/.test(value);
const link = raw => {
  try {
    const url = new URL(String(raw));
    return url.protocol === 'https:' && !url.username && !url.password ? url.href : '';
  } catch { return ''; }
};
const formats = {site:'Site vitrine', paiement:'Site avec paiement', application:'Application',
  encart:'Encart publicitaire', carte:'Carte de visite', qr:'Support QR', vetement:'Vêtement',
  goodie:'Accessoire ou goodie', reseaux:'Kit réseaux automatisé'};
const themes = new Set(['net','chaleur','premium']);
const cookie = (key, age) => '__Host-vm_owner=' + key + '; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=' + age;
const page = (title, content, script = '') => '<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(title)+'</title><link rel="stylesheet" href="/studio.css"><body>'+content+(script?'<script src="'+script+'" defer></script>':'')+'</body></html>';
const gate = (slug = '', bad = false) => page(slug?'Aperçu VM Studio':'Atelier privé VM Studio',
  '<main class="gate"><p class="brand">VM STUDIO <span>ATELIER</span></p><h1>'+(slug?'Votre aperçu privé':'Ouvrir mon atelier')+'</h1><p>'+ (slug?'Entre le code transmis par VM Studio pour voir ta maquette.':'Accès réservé au propriétaire de l’atelier.')+'</p>'+
  (bad?'<p class="error" role="alert">Code invalide ou accès indisponible.</p>':'')+
  '<form method="post" action="'+(slug?'/p/'+e(slug):'/session')+'"><label>Code '+(slug?'client':'atelier')+'<input required type="password" name="code" autocomplete="'+(slug?'off':'current-password')+'" maxlength="120"></label><button>Ouvrir</button></form></main>');
const sessionMs = 12 * 60 * 60 * 1000;
async function bodyText(req, limit) {
  if (!req.body) return '';
  const reader=req.body.getReader(), decoder=new TextDecoder();
  let size=0, text='';
  while (true) {
    const {value,done}=await reader.read();
    if (done) return text+decoder.decode();
    size+=value.byteLength;
    if (size>limit) { await reader.cancel(); return null; }
    text+=decoder.decode(value,{stream:true});
  }
}
const projectUrl = (origin,id) => origin + '/p/' + id;
const safeProject = raw => {
  const kind = Object.hasOwn(formats, raw.kind) ? raw.kind : 'site';
  return {kind, theme:themes.has(raw.theme)?raw.theme:'net', name:text(raw.name,90), title:text(raw.title,105),
    description:text(raw.description,850), services:text(raw.services,700), price:text(raw.price,60),
    cta:text(raw.cta,50), contact:text(raw.contact,150), city:text(raw.city,70),
    photo:validImage(raw.photo)?raw.photo:'', payment:link(raw.payment), qrUrl:link(raw.qrUrl),
    template:text(raw.template,90)};
};
async function qrMarkup(target) {
  const make = (await import('qrcode-generator')).default;
  const code = make(0,'M');
  code.addData(target);
  code.make();
  return code.createSvgTag({cellSize:5,margin:20,alt:'QR vers la destination indiquée'});
}
async function preview(data) {
  const d = safeProject(data);
  const qr = d.kind==='qr' && d.qrUrl ? await qrMarkup(d.qrUrl) : '';
  const blocks = d.services.split('\n').filter(Boolean).slice(0,8);
  return page(d.name, '<main class="preview '+d.theme+' format-'+d.kind+'"><header class="demo"><p class="brand">VM STUDIO <span>APERÇU CLIENT</span></p><p>Maquette · '+e(formats[d.kind])+'</p></header><section class="hero"><div><p class="eyebrow">'+e(d.city||formats[d.kind])+'</p><h1>'+e(d.title||d.name)+'</h1><p class="description">'+e(d.description)+'</p>'+(d.cta?'<span class="mock-cta">'+e(d.cta)+'</span>':'')+(d.price?'<p class="price">'+e(d.price)+'</p>':'')+'</div>'+(d.photo?'<img alt="Photo du projet" src="'+e(d.photo)+'">':'')+'</section>'+
    (blocks.length?'<section class="services"><h2>'+(d.kind==='application'?'Fonctionnalités':'Votre offre')+'</h2><ul>'+blocks.map(item=>'<li>'+e(item)+'</li>').join('')+'</ul></section>':'')+
    '<section class="notes">'+(qr?'<div class="qr">'+qr+'</div>':'')+(d.contact?'<p><strong>Coordonnées</strong> '+e(d.contact)+'</p>':'')+
    (d.kind==='paiement'?'<p><strong>Paiement</strong> '+(d.payment?'Lien renseigné. Transaction désactivée dans cette maquette.':'Emplacement de paiement à relier à votre prestataire.')+'</p>':'')+
    (d.kind==='qr'&&d.qrUrl?'<p><strong>Destination du QR</strong> '+e(d.qrUrl)+'</p>':'')+
    '<p>Une maquette personnalisée par VM Studio.</p></section></main>');
}
export default {
  fetch(request, env) {
    const {pathname} = new URL(request.url);
    if (request.method === 'GET' && (pathname === '/studio.js' || pathname === '/studio.css')) {
      return env.ASSETS.fetch(request);
    }
    return env.STUDIO.get(env.STUDIO.idFromName('atelier-v1')).fetch(request);
  },
};

export class StudioStorage {
  constructor(state, env) {
    this.sql = state.storage.sql;
    this.env = env;
    this.sql.exec(`CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, payload TEXT NOT NULL, salt TEXT NOT NULL, code TEXT NOT NULL, active INTEGER NOT NULL, revision INTEGER NOT NULL, updated INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, expiry INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS throttles (key TEXT PRIMARY KEY, window INTEGER NOT NULL, count INTEGER NOT NULL);`);
  }
  first(query, ...params) { return this.sql.exec(query, ...params).toArray()[0]; }
  async owner(req) {
    const token = (req.headers.get('cookie') || '').match(/(?:^|; )__Host-vm_owner=([0-9a-f]{48})(?:;|$)/)?.[1];
    if (!token) return false;
    return !!this.first('SELECT token FROM sessions WHERE token=? AND expiry>?', await sha(token), Date.now());
  }
  async limited(req, scope, limit) {
    const addr = req.headers.get('cf-connecting-ip') || 'local';
    const key = await sha(addr + '/' + scope);
    const window = Math.floor(Date.now()/900000);
    const result = this.first(`INSERT INTO throttles VALUES(?,?,1)
      ON CONFLICT(key) DO UPDATE SET count=CASE WHEN window=excluded.window THEN count+1 ELSE 1 END, window=excluded.window RETURNING count`, key,window);
    this.sql.exec('DELETE FROM throttles WHERE window<?',window-4);
    return result.count > limit;
  }
  credentials() {
    const stored = this.first("SELECT value FROM settings WHERE key='owner'");
    const config = String(stored?.value || this.env.STUDIO_BOOTSTRAP || '').split(':');
    return config.length===2 && /^[a-f0-9]{32}$/.test(config[0]) && /^[a-f0-9]{64}$/.test(config[1]) ? config : null;
  }
  async issueSession() {
    const token = random();
    this.sql.exec('DELETE FROM sessions WHERE expiry<=?',Date.now());
    this.sql.exec('INSERT INTO sessions VALUES(?,?)',await sha(token),Date.now()+sessionMs);
    return token;
  }
  async fetch(req) {
    try { return await this.route(req); }
    catch (error) {
      if (error instanceof SyntaxError || error instanceof TypeError) return json({error:'Données invalides.'},400);
      console.error('Atelier',error.name);
      return json({error:'Atelier momentanément indisponible.'},503);
    }
  }
  async route(req) {
    const url = new URL(req.url), path=url.pathname, method=req.method;
    if (!['GET','POST'].includes(method)) return json({error:'Méthode indisponible.'},405);
    if (method==='POST' && req.headers.get('origin')!==url.origin) return json({error:'Origine refusée.'},403);
    const client = path.match(/^\/p\/([a-f0-9]{24})$/);
    if (client) {
      const id=client[1];
      if (method==='GET') return html(gate(id));
      if (await this.limited(req,'preview',25)) return html(gate(id,true),429);
      const body = await bodyText(req,512);
      if (body===null) return html(gate(id,true),413);
      const code = text(new URLSearchParams(body).get('code'),120).toUpperCase().replace(/[\s-]/g,'');
      const row = this.first('SELECT payload,salt,code,active,revision FROM projects WHERE id=?',id);
      if (!row?.active || !equal(await sha(row.salt+':'+code),row.code) ||
          !this.first('SELECT id FROM projects WHERE id=? AND active=1 AND revision=?',id,row.revision)) return html(gate(id,true),403);
      return html(await preview(JSON.parse(row.payload)));
    }
    if (path==='/session' && method==='POST') {
      const config=this.credentials();
      if (!config) return html(page('Atelier indisponible','<main class="gate"><h1>Atelier en configuration</h1></main>'),503);
      if (await this.limited(req,'owner',8)) return html(gate('',true),429);
      const body=await bodyText(req,512);
      if (body===null) return html(gate('',true),413);
      const candidate=new URLSearchParams(body).get('code')||'';
      if (candidate.length>120 || !equal(await passwordHash(candidate,config[0]),config[1])
          || this.credentials()?.[1]!==config[1]) return html(gate('',true),403);
      const token=await this.issueSession();
      if (this.credentials()?.[1]!==config[1]) {
        this.sql.exec('DELETE FROM sessions WHERE token=?',await sha(token));
        return html(gate('',true),403);
      }
      return new Response(null,{status:303,headers:{...headers,location:'/atelier','set-cookie':cookie(token,43200)}});
    }
    if (path==='/' && method==='GET') return await this.owner(req)?redirect('/atelier'):html(gate());
    if (path==='/atelier' && method==='GET') {
      if (!await this.owner(req)) return redirect('/');
      const asset=await this.env.ASSETS.fetch(new Request(new URL('/app.html',req.url),{headers:{'accept':'text/html'}}));
      return html(await asset.text(),asset.status);
    }
    if (!path.startsWith('/api/')) return html(page('Introuvable','<main class="gate"><h1>Page introuvable</h1></main>'),404);
    if (!await this.owner(req)) return json({error:'Session expirée.'},401);
    if (path==='/api/projects' && method==='GET') {
      const rows=this.sql.exec("SELECT id,active,revision,updated,json_extract(payload,'$.name') AS name,json_extract(payload,'$.kind') AS kind FROM projects ORDER BY updated DESC LIMIT 200").toArray();
      return json(rows);
    }
    const project=path.match(/^\/api\/projects\/([a-f0-9]{24})(?:\/(rotate|close))?$/);
    if (project && method==='GET' && !project[2]) {
      const row=this.first('SELECT payload,active,revision FROM projects WHERE id=?',project[1]);
      return row?json({data:JSON.parse(row.payload),active:!!row.active,revision:row.revision}):json({error:'Projet introuvable.'},404);
    }
    if (method!=='POST') return json({error:'Route inconnue.'},404);
    if (path==='/api/logout') {
      const token=(req.headers.get('cookie')||'').match(/__Host-vm_owner=([a-f0-9]{48})/)?.[1]||'';
      this.sql.exec('DELETE FROM sessions WHERE token=?',await sha(token));
      return json({},200,{'set-cookie':cookie('',0)});
    }
    const body=await bodyText(req,780000);
    if (body===null) return json({error:'Photo ou formulaire trop volumineux.'},413);
    const input=JSON.parse(body);
    if (path==='/api/password') {
      const current=this.credentials();
      if (await this.limited(req,'owner-password',5)) return json({error:'Réessaie dans quinze minutes.'},429);
      if (!current||typeof input.password!=='string'||input.password.length<20||input.password.length>120||
          typeof input.current!=='string'||input.current.length>120||
          !equal(await passwordHash(input.current,current[0]),current[1])) return json({error:'Code actuel incorrect ou nouveau code trop court (20 caractères minimum).'},400);
      const salt=random(16), hash=await passwordHash(input.password,salt);
      if (this.credentials()?.[1]!==current[1] || !await this.owner(req)) return json({error:'Le code a changé. Reconnecte-toi.'},409);
      this.sql.exec("INSERT INTO settings VALUES('owner',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",salt+':'+hash);
      this.sql.exec('DELETE FROM sessions');
      return json({},200,{'set-cookie':cookie('',0)});
    }
    if (path==='/api/projects' || project) {
      const id=project?.[1] || random(12);
      const mode=project?.[2];
      const row=project&&this.first('SELECT revision,active FROM projects WHERE id=?',id);
      if (project && !row) return json({error:'Projet introuvable.'},404);
      if (row && row.revision!==input.revision) return json({error:'Le projet a changé. Recharge-le avant de poursuivre.'},409);
      let code='';
      let saved;
      if (!project || mode==='rotate') {
        code=random(8).toUpperCase();
        const salt=random(16), hash=await sha(salt+':'+code);
        if (!await this.owner(req)) return json({error:'Session expirée.'},401);
        if (!project) {
          const data=safeProject(input.data||{});
          if (!data.name) return json({error:'Indique le nom du client.'},400);
          saved=this.first('INSERT INTO projects VALUES(?,?,?,?,1,1,?) RETURNING revision,active',id,JSON.stringify(data),salt,hash,Date.now());
        } else {
          saved=this.first('UPDATE projects SET salt=?, code=?, active=1, revision=revision+1, updated=? WHERE id=? AND revision=? RETURNING revision,active',salt,hash,Date.now(),id,input.revision);
        }
      } else if (mode==='close') {
        saved=this.first('UPDATE projects SET active=0,revision=revision+1,updated=? WHERE id=? AND revision=? RETURNING revision,active',Date.now(),id,input.revision);
      } else {
        const data=safeProject(input.data||{});
        if (!data.name) return json({error:'Indique le nom du client.'},400);
        saved=this.first('UPDATE projects SET payload=?,revision=revision+1,updated=? WHERE id=? AND revision=? RETURNING revision,active',JSON.stringify(data),Date.now(),id,input.revision);
      }
      return saved?json({id,code,url:projectUrl(url.origin,id),revision:saved.revision,active:!!saved.active}):
        json({error:'Le projet a changé. Recharge-le.'},409);
    }
    return json({error:'Route inconnue.'},404);
  }
}
