#!/usr/bin/env python3
"""Extrait HTML de brèves sourcées, lisible sans JavaScript sur l'accueil VM.

Aucune requête externe ni publication Meta. Le robot d'actualités réécrit
uniquement la zone balisée du HTML et ne fabrique jamais de titres.
"""
import datetime as dt
import html
import re
from pathlib import Path
from zoneinfo import ZoneInfo

START = "<!-- VM_ACTUS_VISIBLES_START -->"
END = "<!-- VM_ACTUS_VISIBLES_END -->"
IDENT = re.compile(r"[a-z0-9][a-z0-9-]{1,99}\Z")
TZ = ZoneInfo("Europe/Paris")


def render(articles, now=None, max_cards=4):
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        raise ValueError("date avec fuseau requise")
    seen, selected = set(), []
    for row in sorted((a for a in articles if isinstance(a, dict)),
                      key=lambda a: str(a.get("publishedAt") or ""), reverse=True):
        ident = str(row.get("id") or "")
        if not IDENT.fullmatch(ident) or ident in seen:
            continue
        try:
            pub = dt.datetime.fromisoformat(str(row.get("publishedAt")).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        if pub.tzinfo is None or not dt.timedelta(0) <= now - pub <= dt.timedelta(hours=48):
            continue
        sources = row.get("sources") or []
        if not row.get("titre") or not row.get("resume") or not isinstance(sources, list):
            continue
        source = next((s for s in sources if isinstance(s, dict) and s.get("nom") and
                       str(s.get("url") or "").startswith("https://")), None)
        if source is None:
            continue
        seen.add(ident)
        selected.append((row, pub, source))
        if len(selected) == max_cards:
            break
    out = [
        START,
        '<section id="actualites-du-jour" aria-label="Dernières actualités football sourcées" '
        'style="margin:0 0 20px;padding:14px;background:var(--surface);border:2px solid var(--line);border-radius:14px">',
        '<h3 style="font-family:Anton,Impact,sans-serif;margin:0 0 10px;color:var(--ink);font-size:1.35rem">⚡ À LA UNE — ACTUALITÉS SOURCÉES</h3>',
    ]
    if not selected:
        out.append('<p>Les actus du jour arrivent : chaque matin à 5 h, le site repart à neuf. '
                   'En attendant, <a href="/foot-amateur/">le foot amateur de ta région</a> '
                   'et <a href="/actus/">les actus du jour</a>.</p>')
    else:
        out.append('<ul style="list-style:none;padding:0;margin:0;display:grid;gap:10px">')
        for row, pub, source in selected:
            ident = row["id"]
            label = pub.astimezone(TZ).strftime("%d/%m à %Hh%M")
            title = html.escape(str(row["titre"]), quote=True)
            summary = html.escape(str(row["resume"])[:220], quote=True)
            attribution = html.escape(str(source["nom"])[:90], quote=True)
            out.append(
                '<li style="border-bottom:1px solid var(--line);padding-bottom:9px">'
                f'<a href="/a/{ident}.html" style="display:block;font-weight:800;text-decoration:underline;color:var(--ink)">{title}</a>'
                f'<small style="display:block;color:var(--muted)">{label} · Source : {attribution}</small>'
                f'<span style="display:block;color:var(--muted)">{summary}</span>'
                '</li>')
        out.append('</ul>')
        out.append('<p style="margin:10px 0 0"><a href="/#feed-title" style="color:#ff8a97;font-weight:700">Voir toutes les actualités mises à jour</a></p>')
    out += ['</section>', END]
    return "\n".join(out)


def update_index(root, articles, now=None):
    path = Path(root) / "index.html"
    text = path.read_text(encoding="utf-8")
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("Marqueurs d'actualité absents ou répétés dans index.html")
    a, b = text.index(START), text.index(END) + len(END)
    result = text[:a] + render(articles, now=now) + text[b:]
    if result != text:
        path.write_text(result, encoding="utf-8")
        print("Accueil VM : actualités sourcées visibles en HTML, mises à jour.")
        return True
    print("Accueil VM : actualités inchangées.")
    return False
