// VM Prono — étape 1 (mode test).
// Un Worker Cloudflare + un Durable Object (stockage SQLite cohérent) :
//  - conseils publics / VIP saisis et validés par Romain (aucun conseil généré) ;
//  - invitations VIP à usage unique (seul le condensat est stocké, consommation atomique) ;
//  - un seul appareil (session) actif par membre ;
//  - espace administrateur protégé par le secret ADMIN_TOKEN (défini par Romain dans Cloudflare).
// Aucun contenu VIP n'est servi sans session valide.

import { DurableObject } from 'cloudflare:workers';
import { PAGE } from './page.js';

const SESSION_DAYS = 60;
const INVITE_DAYS = 14;
const enc = new TextEncoder();

async function sha256(s) {
  const d = await crypto.subtle.digest('SHA-256', enc.encode(s));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
}
function token(bytes = 20) {
  const a = new Uint8Array(bytes); crypto.getRandomValues(a);
  const alpha = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  return [...a].map((b) => alpha[b % alpha.length]).join('');
}
function safeEqual(a, b) {
  const x = enc.encode(String(a)), y = enc.encode(String(b));
  if (x.length !== y.length) return false;
  let r = 0; for (let i = 0; i < x.length; i++) r |= x[i] ^ y[i];
  return r === 0;
}
function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...headers } });
}
function cookie(name, value, maxAge) {
  return `${name}=${value}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${maxAge}`;
}
function readCookie(req, name) {
  const m = (req.headers.get('cookie') || '').match(new RegExp('(?:^|;\\s*)' + name + '=([A-Za-z0-9]+)'));
  return m ? m[1] : null;
}
function clean(s, max) { return String(s ?? '').replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, max); }

export class Store extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS tips(id TEXT PRIMARY KEY, visibility TEXT NOT NULL, match TEXT NOT NULL, title TEXT NOT NULL,
        body TEXT NOT NULL, odds TEXT, kickoff TEXT, status TEXT NOT NULL DEFAULT 'publie', result TEXT NOT NULL DEFAULT 'en_attente',
        created TEXT NOT NULL, updated TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS members(id TEXT PRIMARY KEY, name TEXT NOT NULL, revoked INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS invites(hash TEXT PRIMARY KEY, member_id TEXT NOT NULL, expires TEXT NOT NULL, used_at TEXT, revoked INTEGER NOT NULL DEFAULT 0);
      CREATE TABLE IF NOT EXISTS sessions(hash TEXT PRIMARY KEY, member_id TEXT NOT NULL UNIQUE, expires TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS attempts(ip TEXT PRIMARY KEY, n INTEGER NOT NULL, since TEXT NOT NULL);
    `);
  }
  now() { return new Date().toISOString(); }
  rows(q, ...a) { return [...this.sql.exec(q, ...a)]; }

  // Limite : 10 tentatives d'activation par IP et par heure.
  limited(ip) {
    const t = Date.now();
    const r = this.rows('SELECT n, since FROM attempts WHERE ip=?', ip)[0];
    if (!r || t - Date.parse(r.since) > 3600e3) { this.sql.exec('INSERT OR REPLACE INTO attempts(ip,n,since) VALUES(?,1,?)', ip, this.now()); return false; }
    if (r.n >= 10) return true;
    this.sql.exec('UPDATE attempts SET n=n+1 WHERE ip=?', ip); return false;
  }
  listTips(vis) {
    return this.rows("SELECT id,visibility,match,title,body,odds,kickoff,result,created FROM tips WHERE status='publie' AND visibility=? ORDER BY created DESC LIMIT 50", vis);
  }
  memberFromSession(hash) {
    const r = this.rows('SELECT s.member_id, s.expires, m.revoked, m.name FROM sessions s JOIN members m ON m.id=s.member_id WHERE s.hash=?', hash)[0];
    if (!r || r.revoked || Date.parse(r.expires) < Date.now()) return null;
    return { id: r.member_id, name: r.name };
  }
  // Consommation atomique : le Durable Object traite les requêtes une par une, et la transaction
  // vérifie « non utilisée, non révoquée, non expirée » avant de marquer l'invitation.
  activate(codeHash, sessionHash) {
    return this.ctx.storage.transactionSync(() => {
      const inv = this.rows('SELECT member_id, expires, used_at, revoked FROM invites WHERE hash=?', codeHash)[0];
      if (!inv || inv.used_at || inv.revoked || Date.parse(inv.expires) < Date.now()) return null;
      const m = this.rows('SELECT revoked FROM members WHERE id=?', inv.member_id)[0];
      if (!m || m.revoked) return null;
      this.sql.exec('UPDATE invites SET used_at=? WHERE hash=? AND used_at IS NULL', this.now(), codeHash);
      // Un seul appareil actif : la nouvelle session remplace l'ancienne.
      this.sql.exec('DELETE FROM sessions WHERE member_id=?', inv.member_id);
      this.sql.exec('INSERT INTO sessions(hash,member_id,expires) VALUES(?,?,?)', sessionHash, inv.member_id,
        new Date(Date.now() + SESSION_DAYS * 864e5).toISOString());
      return inv.member_id;
    });
  }
  async fetch(req) {
    const { op, args } = await req.json();
    const a = args || {};
    switch (op) {
      case 'public': return json({ tips: this.listTips('public') });
      case 'vip': { const m = this.memberFromSession(a.session); return m ? json({ member: m.name, tips: this.listTips('vip') }) : json({ error: 'non_connecte' }, 401); }
      case 'me': { const m = this.memberFromSession(a.session); return json({ vip: !!m, name: m ? m.name : null }); }
      case 'activate': {
        if (this.limited(a.ip)) return json({ error: 'trop_de_tentatives' }, 429);
        const id = this.activate(a.codeHash, a.sessionHash);
        return id ? json({ ok: true }) : json({ error: 'code_invalide' }, 400);
      }
      case 'logout': this.sql.exec('DELETE FROM sessions WHERE hash=?', a.session); return json({ ok: true });
      // --- Administration (déjà authentifiée par le Worker) ---
      case 'state': return json({
        tips: this.rows('SELECT id,visibility,match,title,status,result,created FROM tips ORDER BY created DESC LIMIT 100'),
        members: this.rows("SELECT m.id,m.name,m.revoked,(SELECT COUNT(*) FROM sessions s WHERE s.member_id=m.id) AS appareils FROM members m ORDER BY m.created DESC"),
      });
      case 'addTip': {
        const id = crypto.randomUUID(), t = this.now();
        this.sql.exec('INSERT INTO tips(id,visibility,match,title,body,odds,kickoff,created,updated) VALUES(?,?,?,?,?,?,?,?,?)',
          id, a.visibility === 'vip' ? 'vip' : 'public', clean(a.match, 120), clean(a.title, 120), clean(a.body, 1500),
          clean(a.odds, 20) || null, clean(a.kickoff, 40) || null, t, t);
        return json({ ok: true, id });
      }
      case 'setTip': {
        const status = ['publie', 'retire'].includes(a.status) ? a.status : null;
        const result = ['en_attente', 'gagne', 'perdu', 'annule'].includes(a.result) ? a.result : null;
        if (status) this.sql.exec('UPDATE tips SET status=?, updated=? WHERE id=?', status, this.now(), a.id);
        if (result) this.sql.exec('UPDATE tips SET result=?, updated=? WHERE id=?', result, this.now(), a.id);
        return json({ ok: true });
      }
      case 'invite': {
        const id = crypto.randomUUID();
        this.sql.exec('INSERT INTO members(id,name,created) VALUES(?,?,?)', id, clean(a.name, 60) || 'Membre', this.now());
        this.sql.exec('INSERT INTO invites(hash,member_id,expires) VALUES(?,?,?)', a.codeHash, id, new Date(Date.now() + INVITE_DAYS * 864e5).toISOString());
        return json({ ok: true, member: id });
      }
      case 'reinvite': {
        // Nouveau téléphone : nouvelle invitation pour le même membre (l'ancienne session tombera à l'activation).
        const m = this.rows('SELECT id FROM members WHERE id=? AND revoked=0', a.member)[0];
        if (!m) return json({ error: 'membre_inconnu' }, 404);
        this.sql.exec('UPDATE invites SET revoked=1 WHERE member_id=? AND used_at IS NULL', a.member);
        this.sql.exec('INSERT INTO invites(hash,member_id,expires) VALUES(?,?,?)', a.codeHash, a.member, new Date(Date.now() + INVITE_DAYS * 864e5).toISOString());
        return json({ ok: true });
      }
      case 'revoke': {
        this.sql.exec('UPDATE members SET revoked=1 WHERE id=?', a.member);
        this.sql.exec('DELETE FROM sessions WHERE member_id=?', a.member);
        this.sql.exec('UPDATE invites SET revoked=1 WHERE member_id=? AND used_at IS NULL', a.member);
        return json({ ok: true });
      }
      default: return json({ error: 'operation_inconnue' }, 400);
    }
  }
}

function store(env) { return env.STORE.get(env.STORE.idFromName('vm-prono')); }
async function call(env, op, args) {
  return store(env).fetch('https://store/', { method: 'POST', body: JSON.stringify({ op, args }) });
}
function sameOrigin(req) {
  const o = req.headers.get('origin');
  return !!o && o === new URL(req.url).origin;
}
async function isAdmin(req, env) {
  const c = readCookie(req, 'vmp_admin');
  return !!(c && env.ADMIN_TOKEN && safeEqual(c, await sha256('admin:' + env.ADMIN_TOKEN)));
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const p = url.pathname;
    const sec = { 'x-content-type-options': 'nosniff', 'referrer-policy': 'no-referrer', 'x-frame-options': 'DENY' };
    if (req.method === 'GET' && (p === '/' || p === '/admin')) {
      return new Response(PAGE, { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store',
        'content-security-policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'", ...sec } });
    }
    if (!p.startsWith('/api/')) return new Response('Introuvable', { status: 404 });
    if (req.method !== 'GET' && !sameOrigin(req)) return json({ error: 'origine_refusee' }, 403);
    const session = readCookie(req, 'vmp_s');
    const sessionHash = session ? await sha256('s:' + session) : '';

    if (p === '/api/public' && req.method === 'GET') return call(env, 'public');
    if (p === '/api/me' && req.method === 'GET') return call(env, 'me', { session: sessionHash });
    if (p === '/api/vip' && req.method === 'GET') return call(env, 'vip', { session: sessionHash });
    if (p === '/api/activate' && req.method === 'POST') {
      const body = await req.json().catch(() => ({}));
      const code = clean(body.code, 64).toUpperCase().replace(/[^A-Z0-9]/g, '');
      if (code.length < 16) return json({ error: 'code_invalide' }, 400);
      const newSession = token(32);
      const r = await call(env, 'activate', { ip: req.headers.get('cf-connecting-ip') || 'inconnue',
        codeHash: await sha256('i:' + code), sessionHash: await sha256('s:' + newSession) });
      if (r.status !== 200) return r;
      return json({ ok: true }, 200, { 'set-cookie': cookie('vmp_s', newSession, SESSION_DAYS * 86400) });
    }
    if (p === '/api/logout' && req.method === 'POST') {
      await call(env, 'logout', { session: sessionHash });
      return json({ ok: true }, 200, { 'set-cookie': cookie('vmp_s', '', 0) });
    }
    if (p === '/api/admin/login' && req.method === 'POST') {
      const body = await req.json().catch(() => ({}));
      if (!env.ADMIN_TOKEN) return json({ error: 'admin_non_configure' }, 503);
      if (!safeEqual(String(body.token || ''), env.ADMIN_TOKEN)) return json({ error: 'refuse' }, 403);
      return json({ ok: true }, 200, { 'set-cookie': cookie('vmp_admin', await sha256('admin:' + env.ADMIN_TOKEN), 12 * 3600) });
    }
    if (p.startsWith('/api/admin/')) {
      if (!(await isAdmin(req, env))) return json({ error: 'admin_requis' }, 401);
      const body = req.method === 'POST' ? await req.json().catch(() => ({})) : {};
      if (p === '/api/admin/state') return call(env, 'state');
      if (p === '/api/admin/tip') return call(env, 'addTip', body);
      if (p === '/api/admin/tip-status') return call(env, 'setTip', body);
      if (p === '/api/admin/revoke') return call(env, 'revoke', body);
      if (p === '/api/admin/invite' || p === '/api/admin/reinvite') {
        const code = token(20);
        const r = await call(env, p.endsWith('reinvite') ? 'reinvite' : 'invite', { ...body, codeHash: await sha256('i:' + code) });
        if (r.status !== 200) return r;
        // Le code n'est montré qu'une fois, à Romain ; seul son condensat est stocké.
        return json({ ok: true, code });
      }
    }
    return json({ error: 'introuvable' }, 404);
  },
};
