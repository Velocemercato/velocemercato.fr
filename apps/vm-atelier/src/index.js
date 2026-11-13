// VM Studio (mode test) — un Worker Cloudflare + un Durable Object (SQLite) :
//  /studio      : le client compose son site, voit le prix monter en direct et envoie sa commande ;
//  /salon/<jeton>: « mode salon » : le client voit sur son téléphone ce que Romain construit, en direct ;
//  /voir        : consultation d'un projet avec un code à USAGE UNIQUE (accès perdu à la fermeture) ;
//  /admin       : l'atelier de Romain (protégé par le secret ADMIN_TOKEN défini dans Cloudflare).
// Aucun paiement n'est encaissé ici : Romain valide la commande puis envoie un lien de paiement Stripe.

import { DurableObject } from 'cloudflare:workers';
import { devis } from './prix.js';
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
    `);
  }
  now() { return new Date().toISOString(); }
  rows(q, ...a) { return [...this.sql.exec(q, ...a)]; }
  // Limite simple : n essais par clé et par heure.
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
        if (Number(a.v) === p.version) return json({ v: p.version, same: true });
        return json({ v: p.version, nom: p.nom, doc: JSON.parse(p.doc) });
      }
      // --- Consultation à usage unique : consommation atomique du code, puis session courte.
      case 'ouvrir': {
        if (this.limite('voir:' + a.ip, 10)) return json({ error: 'trop_de_tentatives' }, 429);
        const r = this.ctx.storage.transactionSync(() => {
          const c = this.rows('SELECT projet, expire, utilise, revoque FROM codes WHERE hash=?', a.codeHash)[0];
          if (!c || c.utilise || c.revoque || Date.parse(c.expire) < Date.now()) return null;
          this.sql.exec('UPDATE codes SET utilise=? WHERE hash=? AND utilise IS NULL', this.now(), a.codeHash);
          this.sql.exec('INSERT INTO vues(hash,projet,expire) VALUES(?,?,?)', a.vueHash, c.projet, new Date(Date.now() + VUE_HEURES * 3600e3).toISOString());
          return c.projet;
        });
        if (!r) return json({ error: 'code_invalide' }, 400);
        const p = this.rows('SELECT doc, nom FROM projets WHERE id=?', r)[0];
        return p ? json({ ok: true, nom: p.nom, doc: JSON.parse(p.doc) }) : json({ error: 'code_invalide' }, 400);
      }
      case 'fermer': this.sql.exec('DELETE FROM vues WHERE hash=?', a.vueHash); return json({ ok: true });
      // --- Commande du studio client.
      case 'commande': {
        if (this.limite('cmd:' + a.ip, 5)) return json({ error: 'trop_de_commandes' }, 429);
        const id = crypto.randomUUID().slice(0, 8).toUpperCase();
        this.sql.exec('INSERT INTO commandes(id,cree,contact,config,total) VALUES(?,?,?,?,?)', id, this.now(), JSON.stringify(a.contact), JSON.stringify(a.config), a.total);
        return json({ ok: true, id, total: a.total });
      }
      // --- Administration (déjà authentifiée par le Worker).
      case 'etat': return json({
        projets: this.rows('SELECT id, nom, client, version, salon, maj FROM projets ORDER BY maj DESC LIMIT 200'),
        commandes: this.rows('SELECT id, cree, contact, config, total, statut FROM commandes ORDER BY cree DESC LIMIT 200')
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
        if (!this.rows('SELECT 1 FROM projets WHERE id=?', a.id)[0]) return json({ error: 'introuvable' }, 404);
        this.sql.exec('INSERT INTO codes(hash,projet,expire) VALUES(?,?,?)', a.codeHash, a.id, new Date(Date.now() + CODE_JOURS * 864e5).toISOString());
        return json({ ok: true });
      }
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
const SEC = { 'x-content-type-options': 'nosniff', 'referrer-policy': 'no-referrer' };
function html(corps, cadre = false) {
  return new Response(corps, { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', ...SEC,
    'x-frame-options': cadre ? 'SAMEORIGIN' : 'DENY',
    'content-security-policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'; frame-ancestors " + (cadre ? "'self'" : "'none'") } });
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url), p = url.pathname, ip = req.headers.get('cf-connecting-ip') || 'inconnue';
    if (req.method === 'GET') {
      if (p === '/') return html(pageAccueil);
      if (p === '/studio') return html(pageStudio);
      if (p === '/voir') return html(pageVoir);
      if (p === '/admin') return html(pageAdmin);
      if (/^\/salon\/[A-Z0-9]{24}$/.test(p)) return html(pageSalon, true);
    }
    if (!p.startsWith('/api/')) return new Response('Introuvable', { status: 404 });

    // Lectures publiques.
    if (req.method === 'GET' && p === '/api/config') return json({ email: net(env.CONTACT_EMAIL, 120), tel: net(env.CONTACT_TEL, 40) });
    const ms = p.match(/^\/api\/salon\/([A-Z0-9]{24})$/);
    if (req.method === 'GET' && ms) return appel(env, 'salon', { salon: ms[1], v: url.searchParams.get('v') });
    // Fermeture d'une consultation (envoyée à la fermeture de la page, sans en-tête Origin parfois) : ne fait que supprimer sa propre session.
    if (req.method === 'POST' && p === '/api/voir/fermer') {
      const v = lireCookie(req, 'vma_v');
      if (v) await appel(env, 'fermer', { vueHash: await sha256('v:' + v) });
      return json({ ok: true }, 200, { 'set-cookie': cookie('vma_v', '', 0) });
    }
    if (req.method !== 'GET' && !memeOrigine(req)) return json({ error: 'origine_refusee' }, 403);
    const corps = req.method === 'POST' ? await req.json().catch(() => ({})) : {};

    if (p === '/api/voir/ouvrir' && req.method === 'POST') {
      const code = net(corps.code, 64).toUpperCase().replace(/[^A-Z0-9]/g, '');
      if (code.length < 12) return json({ error: 'code_invalide' }, 400);
      const vue = jeton(32);
      const r = await appel(env, 'ouvrir', { ip, codeHash: await sha256('c:' + code), vueHash: await sha256('v:' + vue) });
      if (r.status !== 200) return r;
      return new Response(r.body, { status: 200, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'set-cookie': cookie('vma_v', vue, VUE_HEURES * 3600) } });
    }
    if (p === '/api/commande' && req.method === 'POST') {
      const c = corps.contact || {};
      const contact = { nom: net(c.nom, 80), email: net(c.email, 120), tel: net(c.tel, 40), message: net(c.message, 1500), projet: net(c.projet, 120) };
      if (!contact.nom || (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact.email) && contact.tel.replace(/\D/g, '').length < 9)) return json({ error: 'contact_incomplet' }, 400);
      if (!corps.cgv) return json({ error: 'conditions_non_acceptees' }, 400);
      const d = devis(corps.config); // total recalculé côté serveur
      return appel(env, 'commande', { ip, contact, config: d, total: d.total });
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
      if (req.method !== 'POST') return json({ error: 'methode' }, 405);
      if (op === 'code') {
        const code = jeton(16);
        const r = await appel(env, 'code', { id: corps.id, codeHash: await sha256('c:' + code) });
        if (r.status !== 200) return r;
        return json({ ok: true, code }); // montré une seule fois à Romain ; seul le condensat est stocké
      }
      if (['creer', 'enregistrer', 'supprimer', 'nouveauSalon', 'statut'].includes(op)) return appel(env, op, corps);
    }
    return json({ error: 'introuvable' }, 404);
  },
};
