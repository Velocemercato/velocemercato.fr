"""Construire les trois fils accessibles depuis le bureau de l’accueil."""

import datetime as dt
from html import escape
import json
import re
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")
FILS = {
    "veloce-mercato": ("Véloce Mercato", "meta/facebook", "Football, mercato et multisport", "/foot/"),
    "vm-univers": ("VM Univers", "meta_univers/facebook", "Les réalisations et services de VM Univers", "https://vmunivers.fr/professionnels/"),
    "vm-actus-pronos": ("VM Actus et Pronos", "meta_pronos/facebook", "Actualité, gaming et sport", "/actus/"),
}
PAGES_FACEBOOK = {
    "veloce-mercato": "https://www.facebook.com/velocemercato.fr/",
    "vm-univers": "https://www.facebook.com/VMunivers.fr/",
    "vm-actus-pronos": "https://www.facebook.com/Veloce.mercato.actus/"
}
SOURCES = {
    "foot": ("articles.json", "/a/"),
    "actus": ("actus/news.json", "/actus/#a="),
    "gaming": ("vm-gaming/news.json", "/vm-gaming/#a="),
}
RUBRIQUES = {
    "foot": ("Football", "/foot/"), "multisport": ("Multisport", "/multisport/"),
    "actus": ("Actualités", "/actus/"), "gaming": ("Gaming", "/vm-gaming/"),
    "belfort": ("VM Belfort", "/belfort/"), "projet": ("Projet VM", "https://vmunivers.fr/"),
}


def lire(path, par_defaut):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else par_defaut


def date_paris(value):
    try:
        date = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return date.astimezone(PARIS).strftime("%d/%m/%Y à %H h %M") if date.tzinfo else ""
    except ValueError:
        return ""


def facebook(url):
    p = urlparse(url or "")
    return (p.scheme == "https" and p.netloc in ("www.facebook.com", "m.facebook.com")
            and bool(re.fullmatch(r"/[^/]+/(?:posts|videos)/[^/]+/?|/reel/[0-9]+/?", p.path)))


def titre_cle(value):
    return re.sub(r"\W+", " ", str(value or "").casefold()).strip()


def index_articles(root):
    indices = {}
    for rubrique, (fichier, base) in SOURCES.items():
        for row in lire(root / fichier, []):
            if not isinstance(row, dict):
                continue
            titre, ident = row.get("titre"), row.get("id")
            if not titre or not re.fullmatch(r"[a-zA-Z0-9_-]+", ident or ""):
                continue
            if rubrique == "foot" and not (root / "a" / (ident + ".html")).is_file():
                continue
            indices[(rubrique, titre_cle(titre))] = base + ident + (".html" if rubrique == "foot" else "")
    for rows in lire(root / "multisport/actualites.json", {}).get("sports", {}).values():
        for row in rows:
            lien = urlparse(row.get("url", ""))
            if lien.scheme == "https" and lien.hostname and not lien.username and not lien.password:
                indices[("multisport", titre_cle(row.get("titre")))] = lien.geturl()
    return indices


def carte(titre, date, etiquette, lien, texte_lien, post=""):
    lien_post = ('<a href="' + escape(post, quote=True)
                 + '" target="_blank" rel="noopener noreferrer">Publication Facebook ↗</a>') if post else ""
    return (
        '<article><p class="meta">' + escape(etiquette) + ' · ' + escape(date) + '</p>'
        + '<h3>' + escape(titre) + '</h3><div class="actions"><a href="' + escape(lien, quote=True) + '">'
        + escape(texte_lien) + '</a>' + lien_post + '</div></article>'
    )


def preparer_fils_bureau(root):
    confirmees = lire(root / "studio/editorial-status.json", {}).get("confirmed", [])
    export = lire(root / "assets/reseaux-publications.json", {})
    locaux = lire(root / "belfort/actus.json", {}).get("titres", [])
    index = index_articles(root)
    for slug, (nom, compte, intro, rubrique) in FILS.items():
        cartes = []
        vus = set()
        for row in sorted(confirmees, key=lambda r: str(r.get("date", "")), reverse=True):
            categorie, post = row.get("section"), row.get("url", "")
            if row.get("target") != compte or categorie not in RUBRIQUES or not facebook(post) or post in vus:
                continue
            titre = row.get("title") or "Publication de " + nom
            badge, rubrique_source = RUBRIQUES[categorie]
            lien = index.get((categorie, titre_cle(titre)), "")
            cartes.append(carte(titre, date_paris(row.get("date")), badge,
                               lien or rubrique_source, "Lire l’article" if lien else "Voir la rubrique", post))
            vus.add(post)
            if len(cartes) == 6:
                break
        derniere = export.get(compte, {})
        lien_recent = derniere.get("url", "")
        chapeau = ('<p class="recent"><a href="' + escape(lien_recent, quote=True)
                   + '" target="_blank" rel="noopener noreferrer">Lire la dernière publication sur Facebook ↗</a>'
                   + '<span>' + escape(date_paris(derniere.get("date"))) + '</span></p>') if facebook(lien_recent) else ""
        if not cartes and not chapeau:
            cartes.append('<p class="note">Aucune publication de la rédaction vérifiée pour le moment.</p>')
        local = ""
        if slug == "vm-univers":
            cartes_locales = []
            for row in locaux[:5]:
                url = urlparse(row.get("u", ""))
                if url.scheme == "https" and url.hostname and not url.username and not url.password:
                    cartes_locales.append(carte(row.get("t", ""), date_paris(row.get("d")), row.get("s") or "VM Belfort",
                                                url.geturl(), "Lire l’article source"))
            if cartes_locales:
                local = ('<section><h2>Dernières actus VM Belfort</h2>'
                         '<p class="note">Actualités du site, indépendamment de la diffusion sur Facebook.</p>'
                         + '<div class="cartes">' + "".join(cartes_locales) + '</div></section>')
        navigation = "".join(
            '<a href="/reseaux/' + autre + '/"' + (' aria-current="page"' if autre == slug else '') + '>'
            + escape(config[0]) + '</a>' for autre, config in FILS.items())
        html = (
            '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            + '<title>' + escape(nom) + ' · Dernières publications</title>'
            + '<link rel="stylesheet" href="/assets/reseaux-bureau.css"></head><body><main>'
            + '<nav aria-label="Fils du bureau">' + navigation + '</nav><header><p class="meta">Publications de la rédaction</p><h1>'
            + escape(nom) + '</h1><p>' + escape(intro) + '</p><div class="actions">'
            + '<a href="' + rubrique + '">Découvrir la rubrique</a>'
            + '<a href="' + PAGES_FACEBOOK[slug] + '" target="_blank" rel="noopener noreferrer">Page Facebook officielle ↗</a>'
            + '<a href="/">Retour au bureau</a></div></header>'
            + '<section><h2>Articles publiés par la rédaction</h2>' + chapeau + '<div class="cartes">' + "".join(cartes)
            + '</div></section>' + local + '</main></body></html>'
        )
        destination = root / "reseaux" / slug / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(html, encoding="utf-8")
