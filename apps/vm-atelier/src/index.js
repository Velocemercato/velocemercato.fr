// VM Studio (mode test) — un Worker Cloudflare + un Durable Object (SQLite) :
//  /studio      : le client compose son site, voit le prix monter en direct et envoie sa commande ;
//  /salon/<jeton>: « mode salon » : le client voit sur son téléphone ce que Romain construit, en direct ;
//  /voir        : consultation d'un projet avec un code à USAGE UNIQUE (accès perdu à la fermeture) ;
//  /admin       : l'atelier de Romain (protégé par le secret ADMIN_TOKEN défini dans Cloudflare).
// Aucun paiement n'est encaissé ici : Romain valide la commande puis envoie un lien de paiement Stripe.

import { DurableObject } from 'cloudflare:workers';
import { devis } from './prix.js';
import { proposer, iaConfiguree, fournisseur, modele } from './ia.js';
import { creerPaiement, verifierPaiement, stripeConfigure, modeStripe } from './paiement.js';
import { pageStudio, pageSalon, pageVoir, pageAdmin, pageAccueil } from './pages.js';

const CODE_JOURS = 7;        // validité d'un code de consultation non utilisé
const VUE_HEURES = 2;        // durée maximale d'une consultation ouverte
const DOC_MAX = 1_500_000;   // taille maximale d'un projet (photos comprises)
const enc = new TextEncoder();

async function sha256(s) {
  const d = await crypto.subtle.digest('SHA-256', enc.encode(s));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
}
function jeton(n = 20) {
  const a = new Uint8Array(n); crypto.getRandomValues(a);
  const alpha = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  return [...a].map((b) => alpha[b % alpha.length]).join('');
}
function egal(a, b) {
  const x = enc.encode(String(a)), y = enc.encode(String(b));
  if (x.length !== y.length) return false;
  let r = 0; for (let i = 0; i < x.length; i++) r |= x[i] ^ y[i];
  return r === 0;
}
function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...headers } });
}
function cookie(nom, val, age) { return `${nom}=${val}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${age}`; }
function lireCookie(req, nom) {
  const m = (req.headers.get('cookie') || '').match(new RegExp('(?:^|;\\s*)' + nom + '=([A-Za-z0-9]+)'));
  return m ? m[1] : null;
}
function net(s, max) { return String(s ?? '').replace(/[\u0000-\u0008\u000b-\u001f\u007f]/g, ' ').trim().slice(0, max); }

// Projet vide de départ (page vierge).
const VIERGE = { theme: { c1: '#e52643', c2: '#f4cf55', fond: '#0b0c12', texte: '#ffffff' }, blocs: [] };

function docValide(doc) {
  if (!doc || typeof doc !== 'object' || !Array.isArray(doc.blocs) || doc.blocs.length > 60) return null;
  const s = JSON.stringify(doc);
  return s.length <= DOC_MAX ? s : null;
}

export class Store extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS projets(id TEXT PRIMARY KEY, nom TEXT NOT NULL, client TEXT NOT NULL DEFAULT '', doc TEXT NOT NULL,
        version INTEGER NOT NULL DEFAULT 1, salon TEXT NOT NULL UNIQUE, cree TEXT NOT NULL, maj TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS codes(hash TEXT PRIMARY KEY, projet TEXT NOT NULL, expire TEXT NOT NULL, utilise TEXT, revoque INTEGER NOT NULL DEFAULT 0);
      CREATE TABLE IF NOT EXISTS vues(hash TEXT PRIMARY KEY, projet TEXT NOT NULL, expire TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS commandes(id TEXT PRIMARY KEY, cree TEXT NOT NULL, contact TEXT NOT NULL, config TEXT NOT NULL,
        total INTEGER NOT NULL, statut TEXT NOT NULL DEFAULT 'nouvelle');
      CREATE TABLE IF NOT EXISTS essais(cle TEXT PRIMARY KEY, n INTEGER NOT NULL, depuis TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS ia_jour(jour TEXT PRIMARY KEY, n INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS ia_journal(cree TEXT NOT NULL, projet TEXT, resultat TEXT NOT NULL, entree INTEGER, sortie INTEGER, modele TEXT);
      CREATE TABLE IF NOT EXISTS avis(id TEXT PRIMARY KEY, projet TEXT NOT NULL, bloc INTEGER, texte TEXT NOT NULL, cree TEXT NOT NULL, traite INTEGER NOT NULL DEFAULT 0);
    `);
  }
  now() { return new Date().toISOString(); }
  colonnesCodes() {
    for (const c of ['mode TEXT', 'session_min INTEGER', 'figee TEXT', 'cree TEXT', 'nb INTEGER DEFAULT 0', 'libelle TEXT'])
      try { this.sql.exec('ALTER TABLE codes ADD COLUMN ' + c); } catch (e) { /* déjà présente */ }
    try { this.sql.exec('ALTER TABLE vues ADD COLUMN code TEXT'); } catch (e) { /* déjà présente */ }
  }
  docVue(code, projet) {
    const c = this.rows('SELECT figee FROM codes WHERE hash=?', code)[0];
    if (c && c.figee) return JSON.parse(c.figee);
    const p = this.rows('SELECT doc FROM projets WHERE id=?', projet)[0];
    return p ? JSON.parse(p.doc) : null;
  }
  colonneProjet() {
    for (const c of ['projet TEXT', 'paiement_session TEXT', 'paiement_url TEXT', 'paye_le TEXT'])
      try { this.sql.exec('ALTER TABLE commandes ADD COLUMN ' + c); } catch (e) { /* déjà présente */ }
  }
  rows(q, ...a) { return [...this.sql.exec(q, ...a)]; }
  // Limite simple : n essais par clé et par heure.
  // Anti force brute : seuls les ÉCHECS comptent (10 mauvais codes par heure et par IP).
  bloque(cle, max) { const r = this.rows('SELECT n, depuis FROM essais WHERE cle=?', cle)[0]; return !!(r && Date.now() - Date.parse(r.depuis) <= 3600e3 && r.n >= max); }
  echec(cle) {
    const r = this.rows('SELECT n, depuis FROM essais WHERE cle=?', cle)[0];
    if (!r || Date.now() - Date.parse(r.depuis) > 3600e3) this.sql.exec('INSERT OR REPLACE INTO essais(cle,n,depuis) VALUES(?,1,?)', cle, this.now());
    else this.sql.exec('UPDATE essais SET n=n+1 WHERE cle=?', cle);
  }
  limite(cle, max) {
    const r = this.rows('SELECT n, depuis FROM essais WHERE cle=?', cle)[0];
    if (!r || Date.now() - Date.parse(r.depuis) > 3600e3) { this.sql.exec('INSERT OR REPLACE INTO essais(cle,n,depuis) VALUES(?,1,?)', cle, this.now()); return false; }
    if (r.n >= max) return true;
    this.sql.exec('UPDATE essais SET n=n+1 WHERE cle=?', cle); return false;
  }
  async fetch(req) {
    const { op, a = {} } = await req.json();
    switch (op) {
      // --- Mode salon : lecture seule par jeton secret, avec numéro de version pour ne rien renvoyer si rien n'a changé.
      case 'salon': {
        const p = this.rows('SELECT doc, version, nom FROM projets WHERE salon=?', a.salon)[0];
        if (!p) return json({ error: 'lien_invalide' }, 404);
        this.colonneProjet();
        const pid = this.rows('SELECT id FROM projets WHERE salon=?', a.salon)[0].id;
        const cmd = this.rows('SELECT id, total, statut, paiement_url FROM commandes WHERE projet=? ORDER BY cree DESC LIMIT 1', pid)[0];
        const paiement = cmd ? { commande: cmd.id, total: cmd.total, paye: cmd.statut === 'payee' || cmd.statut === 'livree', url: cmd.statut === 'payee' || cmd.statut === 'livree' ? null : cmd.paiement_url } : null;
        if (Number(a.v) === p.version) return json({ v: p.version, same: true, paiement });
        return json({ v: p.version, nom: p.nom, doc: JSON.parse(p.doc), paiement });
      }
      // --- Consultation à usage unique : consommation atomique du code, puis session courte.
      case 'ouvrir': {
        if (this.bloque('voir:' + a.ip, 10)) return json({ error: 'trop_de_tentatives' }, 429);
        this.colonnesCodes();
        // Échange atomique : un code « unique » ne s'ouvre qu'une fois (deux ouvertures simultanées → une seule session).
        const r = this.ctx.storage.transactionSync(() => {
          const c = this.rows('SELECT projet, expire, utilise, revoque, mode, session_min FROM codes WHERE hash=?', a.codeHash)[0];
          if (!c || c.revoque || Date.parse(c.expire) < Date.now()) return null;
          if ((c.mode || 'unique') === 'unique') {
            if (c.utilise) return null;
            this.sql.exec('UPDATE codes SET utilise=?, nb=1 WHERE hash=? AND utilise IS NULL', this.now(), a.codeHash);
          } else this.sql.exec('UPDATE codes SET nb=COALESCE(nb,0)+1, utilise=COALESCE(utilise,?) WHERE hash=?', this.now(), a.codeHash);
          const fin = Math.min(Date.now() + (c.session_min || VUE_HEURES * 60) * 60e3, Date.parse(c.expire) + (c.session_min || 120) * 60e3);
          this.sql.exec('INSERT INTO vues(hash,projet,expire,code) VALUES(?,?,?,?)', a.vueHash, c.projet, new Date(fin).toISOString(), a.codeHash);
          return { projet: c.projet, fin };
        });
        if (!r) { this.echec('voir:' + a.ip); return json({ error: 'code_invalide' }, 400); }
        const p = this.rows('SELECT nom FROM projets WHERE id=?', r.projet)[0];
        const doc = this.docVue(a.codeHash, r.projet);
        return p && doc ? json({ ok: true, nom: p.nom, doc, fin: new Date(r.fin).toISOString(), duree: Math.round((r.fin - Date.now()) / 1000) }) : json({ error: 'code_invalide' }, 400);
      }
      // Session de consultation en cours (l'actualisation de la page fonctionne jusqu'à la fin de la session).
      case 'vue': {
        this.colonnesCodes();
        const v = this.rows('SELECT projet, expire, code FROM vues WHERE hash=?', a.vueHash)[0];
        if (!v || Date.parse(v.expire) < Date.now()) return json({ error: 'session_terminee' }, 410);
        const c = v.code ? this.rows('SELECT revoque FROM codes WHERE hash=?', v.code)[0] : null;
        if (c && c.revoque) return json({ error: 'session_terminee' }, 410);
        const p = this.rows('SELECT nom FROM projets WHERE id=?', v.projet)[0];
        const doc = this.docVue(v.code, v.projet);
        return p && doc ? json({ ok: true, nom: p.nom, doc, fin: v.expire }) : json({ error: 'session_terminee' }, 410);
      }
      case 'fermer': this.sql.exec('DELETE FROM vues WHERE hash=?', a.vueHash); return json({ ok: true });
      // --- Retours du client depuis son lien salon (« non, je veux ça là »).
      case 'avisAjouter': {
        const p = this.rows('SELECT id FROM projets WHERE salon=?', a.salon)[0];
        if (!p) return json({ error: 'lien_invalide' }, 404);
        if (this.limite('avis:' + a.ip, 30)) return json({ error: 'trop_de_messages' }, 429);
        const texte = net(a.texte, 600); if (!texte) return json({ error: 'message_vide' }, 400);
        const bloc = Number.isInteger(a.bloc) && a.bloc >= 0 && a.bloc < 100 ? a.bloc : null;
        this.sql.exec('INSERT INTO avis(id,projet,bloc,texte,cree) VALUES(?,?,?,?,?)', crypto.randomUUID(), p.id, bloc, texte, this.now());
        return json({ ok: true });
      }
      case 'lireCommande': {
        this.colonneProjet();
        const c = this.rows('SELECT * FROM commandes WHERE id=?', a.id)[0];
        return c ? json({ ...c, contact: JSON.parse(c.contact), config: JSON.parse(c.config) }) : json({ error: 'introuvable' }, 404);
      }
      case 'paiementEnregistrer':
        this.colonneProjet(); this.sql.exec('UPDATE commandes SET paiement_session=?, paiement_url=? WHERE id=?', a.session, a.url, a.id); return json({ ok: true });
      case 'marquerPayee': // idempotent : un paiement confirmé deux fois ne change rien
        this.colonneProjet(); this.sql.exec("UPDATE commandes SET statut='payee', paye_le=? WHERE id=? AND statut IN ('nouvelle','validee')", this.now(), a.id); return json({ ok: true });
      case 'avisListe': return json({ avis: this.rows('SELECT id, bloc, texte, cree, traite FROM avis WHERE projet=? ORDER BY cree DESC LIMIT 50', a.id) });
      case 'avisTraite': this.sql.exec('UPDATE avis SET traite=1 WHERE id=?', a.avis); return json({ ok: true });
      // --- Plafond quotidien d'appels IA (réservation atomique avant l'appel payant).
      case 'iaReserver': {
        const jour = this.now().slice(0, 10), max = Math.max(1, Number(a.max) || 40);
        const ok = this.ctx.storage.transactionSync(() => {
          const r = this.rows('SELECT n FROM ia_jour WHERE jour=?', jour)[0];
          if (r && r.n >= max) return false;
          this.sql.exec('INSERT INTO ia_jour(jour,n) VALUES(?,1) ON CONFLICT(jour) DO UPDATE SET n=n+1', jour); return true;
        });
        return ok ? json({ ok: true }) : json({ error: 'ia_plafond' }, 429);
      }
      case 'iaJournal':
        this.sql.exec('INSERT INTO ia_journal(cree,projet,resultat,entree,sortie,modele) VALUES(?,?,?,?,?,?)', this.now(), a.id || null, net(a.resultat, 40), a.entree || 0, a.sortie || 0, net(a.modele, 60));
        return json({ ok: true });
      case 'iaEtat': {
        const r = this.rows('SELECT n FROM ia_jour WHERE jour=?', this.now().slice(0, 10))[0];
        return json({ utilises: r ? r.n : 0, journal: this.rows('SELECT cree, resultat, entree, sortie, modele FROM ia_journal ORDER BY cree DESC LIMIT 10') });
      }
      // --- Commande du studio client.
      case 'commande': {
        if (this.limite('cmd:' + a.ip, 5)) return json({ error: 'trop_de_commandes' }, 429);
        const id = crypto.randomUUID().slice(0, 8).toUpperCase();
        this.colonneProjet();
        // Le site composé par le client est sauvegardé comme projet : Romain le retrouve dans l'atelier,
        // le corrige, et le client suit les corrections en direct avec son lien.
        let projet = null, salon = null;
        if (a.doc) {
          projet = crypto.randomUUID(); salon = jeton(24); const t = this.now();
          this.sql.exec('INSERT INTO projets(id,nom,client,doc,salon,cree,maj) VALUES(?,?,?,?,?,?,?)', projet,
            net(a.contact.projet, 80) || ('Commande ' + id), net(a.contact.nom, 80), a.doc, salon, t, t);
        }
        this.sql.exec('INSERT INTO commandes(id,cree,contact,config,total,projet) VALUES(?,?,?,?,?,?)', id, this.now(), JSON.stringify(a.contact), JSON.stringify(a.config), a.total, projet);
        return json({ ok: true, id, total: a.total, salon });
      }
      // --- Administration (déjà authentifiée par le Worker).
      case 'etat': this.colonneProjet(); return json({
        projets: this.rows('SELECT id, nom, client, version, salon, maj FROM projets ORDER BY maj DESC LIMIT 200'),
        commandes: this.rows('SELECT id, cree, contact, config, total, statut, projet, paiement_session, paiement_url, paye_le FROM commandes ORDER BY cree DESC LIMIT 200')
          .map((c) => ({ ...c, contact: JSON.parse(c.contact), config: JSON.parse(c.config) })),
      });
      case 'creer': {
        const id = crypto.randomUUID(), t = this.now();
        this.sql.exec('INSERT INTO projets(id,nom,client,doc,salon,cree,maj) VALUES(?,?,?,?,?,?,?)', id, net(a.nom, 80) || 'Nouveau projet',
          net(a.client, 80), JSON.stringify(VIERGE), jeton(24), t, t);
        return json({ ok: true, id });
      }
      case 'lire': {
        const p = this.rows('SELECT id, nom, client, doc, version, salon FROM projets WHERE id=?', a.id)[0];
        return p ? json({ ...p, doc: JSON.parse(p.doc) }) : json({ error: 'introuvable' }, 404);
      }
      case 'enregistrer': {
        const s = docValide(a.doc);
        if (!s) return json({ error: 'projet_trop_lourd_ou_invalide' }, 400);
        if (a.base != null) {
          const cur = this.rows('SELECT version FROM projets WHERE id=?', a.id)[0];
          if (cur && cur.version !== Number(a.base)) return json({ error: 'projet_modifie', v: cur.version }, 409);
        }
        this.sql.exec('UPDATE projets SET doc=?, version=version+1, maj=?, nom=COALESCE(NULLIF(?,\'\'),nom) WHERE id=?', s, this.now(), net(a.nom, 80), a.id);
        const v = this.rows('SELECT version FROM projets WHERE id=?', a.id)[0];
        return v ? json({ ok: true, v: v.version }) : json({ error: 'introuvable' }, 404);
      }
      case 'supprimer':
        this.sql.exec('DELETE FROM projets WHERE id=?', a.id); this.sql.exec('UPDATE codes SET revoque=1 WHERE projet=?', a.id);
        this.sql.exec('DELETE FROM vues WHERE projet=?', a.id); return json({ ok: true });
      case 'nouveauSalon': // coupe l'ancien lien salon
        this.sql.exec('UPDATE projets SET salon=? WHERE id=?', jeton(24), a.id); return json({ ok: true });
      case 'code': {
        this.colonnesCodes();
        const p = this.rows('SELECT doc FROM projets WHERE id=?', a.id)[0];
        if (!p) return json({ error: 'introuvable' }, 404);
        const jours = [1, 7, 30].includes(Number(a.jours)) ? Number(a.jours) : CODE_JOURS;
        const min = [15, 60, 1440].includes(Number(a.minutes)) ? Number(a.minutes) : 15;
        const mode = a.mode === 'multi' ? 'multi' : 'unique';
        this.sql.exec('INSERT INTO codes(hash,projet,expire,mode,session_min,figee,cree,libelle) VALUES(?,?,?,?,?,?,?,?)', a.codeHash, a.id,
          new Date(Date.now() + jours * 864e5).toISOString(), mode, min, a.figee ? p.doc : null, this.now(), net(a.libelle, 60));
        return json({ ok: true, expire: new Date(Date.now() + jours * 864e5).toISOString(), mode, minutes: min });
      }
      case 'codesListe':
        this.colonnesCodes();
        return json({ codes: this.rows("SELECT substr(hash,1,12) AS ref, expire, utilise, revoque, mode, session_min, (figee IS NOT NULL) AS figee, cree, nb, libelle FROM codes WHERE projet=? ORDER BY cree DESC LIMIT 30", a.id) });
      case 'codeRevoquer':
        this.colonnesCodes();
        this.sql.exec('UPDATE codes SET revoque=1 WHERE projet=? AND substr(hash,1,12)=?', a.id, a.ref);
        this.sql.exec('DELETE FROM vues WHERE code IN (SELECT hash FROM codes WHERE projet=? AND substr(hash,1,12)=?)', a.id, a.ref);
        return json({ ok: true });
      case 'statut': {
        const ok = ['nouvelle', 'validee', 'payee', 'livree', 'annulee'];
        if (!ok.includes(a.statut)) return json({ error: 'statut_invalide' }, 400);
        this.sql.exec('UPDATE commandes SET statut=? WHERE id=?', a.statut, a.id); return json({ ok: true });
      }
      default: return json({ error: 'operation_inconnue' }, 400);
    }
  }
}

function appel(env, op, a) {
  return env.STORE.get(env.STORE.idFromName('vm-atelier')).fetch('https://store/', { method: 'POST', body: JSON.stringify({ op, a }) });
}
function memeOrigine(req) { const o = req.headers.get('origin'); return !!o && o === new URL(req.url).origin; }
async function estAdmin(req, env) {
  const c = lireCookie(req, 'vma_admin');
  return !!(c && env.ADMIN_TOKEN && egal(c, await sha256('admin:' + env.ADMIN_TOKEN)));
}
// Seul domaine VM vérifié pour les liens clients (salon, code unique) : jamais l'adresse technique workers.dev.
const DOMAINE = 'https://atelier.velocemercato.fr';
const SEC = { 'x-content-type-options': 'nosniff', 'referrer-policy': 'no-referrer' };
function html(corps, cadre = false) {
  return new Response(corps, { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', ...SEC,
    'x-frame-options': cadre ? 'SAMEORIGIN' : 'DENY',
    'content-security-policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'; frame-ancestors " + (cadre ? "'self'" : "'none'") } });
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url), p = url.pathname, ip = req.headers.get('cf-connecting-ip') || 'inconnue';
    // L'adresse technique *.workers.dev redirige vers le domaine VM vérifié (mêmes chemins).
    if (url.hostname.endsWith('.workers.dev') && !env.AUTORISER_WORKERS_DEV) return Response.redirect(DOMAINE + p + url.search, 301);
    if (req.method === 'GET' || req.method === 'HEAD') { // HEAD (aperçus de liens, robots) : page servie, rien n'est consommé
      if (p === '/') return html(pageAccueil);
      if (p === '/studio') return html(pageStudio);
      if (p === '/voir') return html(pageVoir);
      if (p === '/admin') return html(pageAdmin);
      if (/^\/salon\/[A-Z0-9]{24}$/.test(p)) return html(pageSalon, true);
      if (p === '/paiement/retour') {
        const id = net(url.searchParams.get('c'), 20);
        const c = await (await appel(env, 'lireCommande', { id })).json();
        let paye = false;
        if (!c.error && c.paiement_session) { const v = await verifierPaiement(env, c.paiement_session); paye = v.paye; if (paye) await appel(env, 'marquerPayee', { id }); }
        if (!c.error && (c.statut === 'payee' || c.statut === 'livree')) paye = true;
        const titre = paye ? '✅ Paiement reçu, merci !' : (url.searchParams.get('annule') ? 'Paiement annulé' : 'Paiement non confirmé');
        const texte = paye ? 'Votre commande n° ' + (c.id || '') + ' est payée. Le créateur finalise votre site et le met en ligne.' : 'Aucun montant n’a été débité. Vous pouvez réessayer depuis votre lien de suivi.';
        return html('<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Paiement — VM Studio</title></head><body style="margin:0;background:#07080d;color:#f3f4f8;font:17px/1.5 system-ui;display:grid;place-items:center;min-height:100vh"><main style="max-width:520px;padding:24px;text-align:center"><h1>' + titre + '</h1><p>' + texte + '</p></main></body></html>');
      }
    }
    if (!p.startsWith('/api/')) return new Response('Introuvable', { status: 404 });

    // Lectures publiques.
    if (req.method === 'GET' && p === '/api/config') return json({ email: net(env.CONTACT_EMAIL, 120), tel: net(env.CONTACT_TEL, 40), domaine: env.DOMAINE_LIENS || DOMAINE });
    const ms = p.match(/^\/api\/salon\/([A-Z0-9]{24})$/);
    if (req.method === 'GET' && ms) return appel(env, 'salon', { salon: ms[1], v: url.searchParams.get('v') });
    // Fermeture d'une consultation (envoyée à la fermeture de la page, sans en-tête Origin parfois) : ne fait que supprimer sa propre session.
    if (req.method === 'POST' && p === '/api/voir/fermer') {
      const v = lireCookie(req, 'vma_v');
      if (v) await appel(env, 'fermer', { vueHash: await sha256('v:' + v) });
      return json({ ok: true }, 200, { 'set-cookie': cookie('vma_v', '', 0) });
    }
    // Formulaire « Votre projet » de vmunivers.fr / velocemercato.fr : la demande arrive dans l'atelier (onglet Commandes).
    if (p === '/api/demande') {
      const o = req.headers.get('origin') || '';
      const permis = /^https:\/\/(www\.)?(vmunivers\.fr|velocemercato\.fr)$/.test(o);
      const cors = permis ? { 'access-control-allow-origin': o, 'access-control-allow-methods': 'POST', 'access-control-allow-headers': 'content-type, accept', vary: 'Origin' } : {};
      if (req.method === 'OPTIONS') return new Response(null, { status: permis ? 204 : 403, headers: cors });
      if (req.method !== 'POST' || !permis) return json({ success: false, error: 'origine_refusee' }, 403, cors);
      const d = await req.json().catch(() => ({}));
      if (d._honey) return json({ success: false }, 400, cors);
      const contact = { nom: net(d.nom, 80), email: net(d.email, 120), tel: net(d.tel, 40),
        message: net([d.besoin_principal && 'Besoin : ' + d.besoin_principal, d.ville && 'Ville : ' + d.ville, d.delai && 'Délai : ' + d.delai, d.projet].filter(Boolean).join('\n'), 1500),
        projet: net(d.besoin_principal, 120), origine: o };
      if (!contact.nom || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact.email)) return json({ success: false, error: 'contact_incomplet' }, 400, cors);
      if (d.consentement !== 'oui') return json({ success: false, error: 'consentement' }, 400, cors);
      const r = await (await appel(env, 'commande', { ip, contact, config: { lignes: [], total: 0, type: 'demande' }, total: 0 })).json();
      return json({ success: !!r.ok, id: r.id }, r.ok ? 200 : 429, cors);
    }
    if (req.method !== 'GET' && !memeOrigine(req)) return json({ error: 'origine_refusee' }, 403);
    const mav = p.match(/^\/api\/salon\/([A-Z0-9]{24})\/avis$/);
    if (req.method === 'POST' && mav) {
      const c = await req.json().catch(() => ({}));
      return appel(env, 'avisAjouter', { salon: mav[1], ip, texte: c.texte, bloc: c.bloc });
    }
    const corps = req.method === 'POST' ? await req.json().catch(() => ({})) : {};

    if (p === '/api/voir/ouvrir' && req.method === 'POST') {
      const code = net(corps.code, 64).toUpperCase().replace(/[^A-Z0-9]/g, '');
      if (code.length < 12) return json({ error: 'code_invalide' }, 400);
      const vue = jeton(32);
      const r = await appel(env, 'ouvrir', { ip, codeHash: await sha256('c:' + code), vueHash: await sha256('v:' + vue) });
      if (r.status !== 200) return r;
      const j = await r.json();
      return json(j, 200, { 'set-cookie': cookie('vma_v', vue, Math.max(60, j.duree || 900)) });
    }
    if (p === '/api/voir/session' && req.method === 'GET') {
      const v = lireCookie(req, 'vma_v');
      if (!v) return json({ error: 'session_terminee' }, 410);
      return appel(env, 'vue', { vueHash: await sha256('v:' + v) });
    }
    if (p === '/api/commande' && req.method === 'POST') {
      const c = corps.contact || {};
      const contact = { nom: net(c.nom, 80), email: net(c.email, 120), tel: net(c.tel, 40), message: net(c.message, 1500), projet: net(c.projet, 120) };
      if (!contact.nom || (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact.email) && contact.tel.replace(/\D/g, '').length < 9)) return json({ error: 'contact_incomplet' }, 400);
      if (!corps.cgv) return json({ error: 'conditions_non_acceptees' }, 400);
      const d = devis(corps.config); // total recalculé côté serveur
      const docTexte = corps.doc ? docValide(corps.doc) : null; // site composé par le client (photos comprises, taille limitée)
      if (corps.doc && !docTexte) return json({ error: 'site_trop_lourd' }, 400);
      const r = await (await appel(env, 'commande', { ip, contact, config: d, total: d.total, doc: docTexte })).json();
      if (r.salon) r.lien = (env.DOMAINE_LIENS || DOMAINE) + '/salon/' + r.salon;
      delete r.salon;
      return json(r, r.ok ? 200 : 429);
    }
    if (p === '/api/admin/login' && req.method === 'POST') {
      if (!env.ADMIN_TOKEN) return json({ error: 'admin_non_configure' }, 503);
      if (!egal(String(corps.token || ''), env.ADMIN_TOKEN)) return json({ error: 'refuse' }, 403);
      return json({ ok: true }, 200, { 'set-cookie': cookie('vma_admin', await sha256('admin:' + env.ADMIN_TOKEN), 12 * 3600) });
    }
    if (p.startsWith('/api/admin/')) {
      if (!(await estAdmin(req, env))) return json({ error: 'admin_requis' }, 401);
      const op = p.slice('/api/admin/'.length);
      if (op === 'etat' && req.method === 'GET') return appel(env, 'etat');
      if (op === 'lire' && req.method === 'GET') return appel(env, 'lire', { id: url.searchParams.get('id') });
      if (op === 'avis' && req.method === 'GET') return appel(env, 'avisListe', { id: url.searchParams.get('id') });
      if (op === 'codes' && req.method === 'GET') return appel(env, 'codesListe', { id: url.searchParams.get('id') });
      if (op === 'ia-etat' && req.method === 'GET') {
        const e = await (await appel(env, 'iaEtat')).json();
        return json({ stripe: stripeConfigure(env) ? modeStripe(env) : null, configuree: iaConfiguree(env), fournisseur: fournisseur(env), modele: modele(env), plafond: Number(env.IA_MAX_JOUR) || 40, ...e });
      }
      if (req.method !== 'POST') return json({ error: 'methode' }, 405);
      if (op === 'code') {
        const code = jeton(16);
        const r = await appel(env, 'code', { id: corps.id, codeHash: await sha256('c:' + code), jours: corps.jours, minutes: corps.minutes, mode: corps.mode, figee: !!corps.figee, libelle: corps.libelle });
        if (r.status !== 200) return r;
        const info = await r.json();
        return json({ ok: true, code, lien: (env.DOMAINE_LIENS || DOMAINE) + '/voir', ...info }); // code montré une seule fois ; seul le condensat est stocké
      }
      if (op === 'avis-traite') return appel(env, 'avisTraite', { avis: corps.avis });
      if (op === 'code-revoquer') return appel(env, 'codeRevoquer', { id: corps.id, ref: corps.ref });
      if (op === 'paiement') {
        const c = await (await appel(env, 'lireCommande', { id: corps.id })).json();
        if (c.error) return json(c, 404);
        if (c.statut === 'payee' || c.statut === 'livree') return json({ error: 'deja_payee', message: 'Commande déjà payée.' }, 409);
        const r = await creerPaiement(env, c, env.DOMAINE_LIENS || DOMAINE);
        if (!r.ok) return json({ error: r.erreur, message: r.message }, r.erreur === 'stripe_non_connecte' ? 503 : 400);
        await appel(env, 'paiementEnregistrer', { id: c.id, session: r.session, url: r.url });
        return json({ ok: true, url: r.url, mode: r.mode });
      }
      if (op === 'paiement-verifier') {
        const c = await (await appel(env, 'lireCommande', { id: corps.id })).json();
        if (c.error || !c.paiement_session) return json({ paye: false });
        const v = await verifierPaiement(env, c.paiement_session);
        if (v.paye) await appel(env, 'marquerPayee', { id: c.id });
        return json({ paye: v.paye });
      }
      if (op === 'ia') {
        const consigne = net(corps.consigne, 1500);
        if (!consigne) return json({ error: 'consigne_vide' }, 400);
        if (!iaConfiguree(env)) return json({ error: 'ia_non_connectee', message: 'IA à connecter : ajoute le secret GEMINI_API_KEY (gratuit) ou ANTHROPIC_API_KEY sur vm-atelier dans Cloudflare.' }, 503);
        const proj = await (await appel(env, 'lire', { id: corps.id })).json();
        if (proj.error) return json(proj, 404);
        const res = await appel(env, 'iaReserver', { max: Number(env.IA_MAX_JOUR) || 40 });
        if (res.status !== 200) return json({ error: 'ia_plafond', message: 'Plafond d’appels IA du jour atteint.' }, 429);
        const r = await proposer(env, proj.doc, consigne);
        await appel(env, 'iaJournal', { id: corps.id, resultat: r.ok ? 'proposition' : r.erreur, entree: r.usage?.entree, sortie: r.usage?.sortie, modele: r.usage?.modele });
        if (!r.ok) return json({ error: r.erreur, message: r.message }, 502);
        // La proposition n'est PAS enregistrée : Romain la voit, puis l'applique (ou non).
        return json({ ok: true, explication: r.explication, doc: r.doc, base: proj.version });
      }
      if (['creer', 'enregistrer', 'supprimer', 'nouveauSalon', 'statut'].includes(op)) return appel(env, op, corps);
    }
    return json({ error: 'introuvable' }, 404);
  },
};
