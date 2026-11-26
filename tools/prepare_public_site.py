"""Applique les demandes de navigation aux pages du site avant leur publication."""
from html.parser import HTMLParser
from pathlib import Path
import re
import json
from html import escape
import sys
import datetime as dt
from decimal import Decimal
import zipfile
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from urllib.request import urlopen

REMOVE_CLASSES = {'vmbar', 'vmtop', 'vm-volets', 'vm-duo', 'vm-essentiel', 'promo-manga'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


class RemoveNavigation(HTMLParser):
    def __init__(self, multisport=False):
        super().__init__(convert_charrefs=False)
        self.output = []
        self.depth = 0
        self.multisport = multisport

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        discard = bool(REMOVE_CLASSES.intersection(attrs.get('class', '').split()))
        discard = discard or attrs.get('aria-label') == 'Annonce VM MANGAS' or (self.multisport and tag == 'a' and attrs.get('data-sport') == 'foot')
        if self.depth or discard:
            if tag not in VOID:
                self.depth += 1
            return
        self.output.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if not self.depth:
            self.output.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.depth:
            if tag not in VOID:
                self.depth -= 1
            return
        self.output.append(f'</{tag}>')

    def handle_data(self, text):
        if not self.depth:
            self.output.append(text)

    def handle_entityref(self, name):
        self.handle_data('&' + name + ';')

    def handle_charref(self, name):
        self.handle_data('&#' + name + ';')

    def handle_comment(self, text):
        if not self.depth:
            self.output.append('<!--' + text + '-->')

    def handle_decl(self, text):
        if not self.depth:
            self.output.append('<!' + text + '>')


def _prepare_affiches(root):
    """Extraire les affiches et les afficher dans l’espace Conseils uniquement."""
    sys.path.insert(0, str(root))
    from tools.pronos_public import section_affiches_publiques
    config_path = root / "pronos/affiches-public.json"
    archive_path = root / "pronos/affiches/affiches-veloce-14-novembre-2026.zip"
    page = root / "conseils/index.html"
    if not (config_path.is_file() and archive_path.is_file() and page.is_file()):
        return
    data = json.loads(config_path.read_text(encoding="utf-8"))
    expected = {str(row["fichier"]) for row in data.get("affiches", []) if isinstance(row, dict) and "fichier" in row}
    if not expected or len(expected) > 4:
        return
    with zipfile.ZipFile(archive_path) as archive:
        members = {info.filename: info for info in archive.infolist()}
        for name in expected:
            if not re.fullmatch(r"[a-z0-9-]+\.jpg", name):
                raise ValueError("Nom d'affiche invalide")
            # L'archive fournie contient des JPEG qui portent, par erreur, le suffixe PNG.
            source_name = name[:-4] + ".png"
            info = members.get(source_name)
            if info is None or info.file_size > 3_500_000:
                raise ValueError("Image attendue manquante ou trop volumineuse")
            data_bytes = archive.read(source_name)
            if not data_bytes.startswith(b"\xff\xd8\xff"):
                raise ValueError("Format JPEG invalide")
            (root / "pronos/affiches" / name).write_bytes(data_bytes)

    galerie = section_affiches_publiques(root, dt.datetime.now(dt.timezone.utc))
    source = page.read_text(encoding="utf-8")
    placeholder = "<!-- VM_AFFICHES_DU_JOUR -->"
    if placeholder not in source:
        raise ValueError("Emplacement de galerie manquant dans conseils/index.html")
    # Les images n'apparaissent jamais dans la rubrique d'actualités générale.
    page.write_text(source.replace(placeholder, galerie), encoding="utf-8")



def _tickets_cumul(records):
    uniques, publics, dates = {}, set(), set()
    for day, item in records:
        for ticket in item.get("tickets_chiffres", []):
            ident, cote, reussi = ticket["id"], ticket["cote_centiemes"], ticket["reussi"]
            valeur = (cote, reussi, ticket.get("direct", False))
            if type(cote) is not int or cote < 100 or type(reussi) is not bool:
                raise ValueError("Cote ou résultat invalide dans le bilan chiffré.")
            if ident in uniques and uniques[ident] != valeur:
                raise ValueError("Résultats divergents pour le même ticket.")
            uniques[ident] = valeur
            dates.add(day)
            if item.get("type") == "public":
                publics.add(ident)
    return uniques, publics, dates


def _rendement(tickets):
    gagnes = [cote for cote, reussi, _ in tickets if reussi]
    return Decimal(sum(gagnes)) / len(tickets) - 100, len(gagnes)


def _resume_public_conseils(records):
    uniques, publics, _ = _tickets_cumul(records)
    if not publics:
        return ""
    tickets = [uniques[i] for i in publics]
    taux, gagnes = _rendement(tickets)
    classe = " negatif" if taux < 0 else " positif" if taux > 0 else ""
    valeur = (format(taux, "+.2f") if taux else "0,00").replace(".", ",")
    return ('<section class="card resume-public-conseils" id="rendement-public" aria-labelledby="rendement-public-titre">'
            '<div><h2 id="rendement-public-titre">Rendement des conseils publics</h2>'
            f'<strong class="taux-public{classe}">{valeur} %</strong>'
            f'<p>{gagnes} sur {len(tickets)} conseils validés · Une même mise simulée par ticket.</p>'
            '<p class="muted">Calcul sur les tickets publics réglés et documentés. Les conseils en cours restent hors du calcul.</p></div>'
            '<a href="#analyse-resultats">Voir le détail du bilan ↗</a></section>')


def _cumul_conseils(records):
    uniques, publics, dates = _tickets_cumul(records)
    if not uniques:
        return ""
    lignes = []
    for titre, tickets in (
        ("Conseils publics", [uniques[i] for i in publics]),
        ("Public et VIP, doublons retirés", list(uniques.values())),
        ("Public et VIP, hors pari en direct", [t for t in uniques.values() if not t[2]]),
    ):
        if not tickets:
            continue
        nombre = len(tickets)
        pourcentage, gagnes = _rendement(tickets)
        affichage = format(pourcentage, "+.2f").replace(".", ",")
        lignes.append(f'<div><dt>{titre}</dt><dd><strong>{affichage} %</strong><span>{gagnes} sur {nombre} validés</span></dd></div>')
    debut, fin = min(dates), max(dates)
    couverture = f'{len(dates)} journées documentées du {debut:%d/%m/%Y} au {fin:%d/%m/%Y}.'
    return ('<section id="analyse-resultats" aria-labelledby="analyse-resultats-titre">'
            '<h3 id="analyse-resultats-titre">Bilan cumulé à mise égale</h3><p>' + couverture + '</p>'
            '<dl class="results-yield">' + ''.join(lignes) + '</dl>'
            '<p>Une unité par ticket et un seul décompte pour chaque ticket partagé en public et en VIP. '
            'Le rendement théorique correspond au total des retours, mises incluses, moins les unités jouées, divisé par les unités jouées. '
            'Le pari en direct à 8,25 augmente sensiblement le cumul. Les journées sans bilan chiffré restent hors de ce calcul.</p>'
            '</section>')


def _prepare_bilan_veille(root):
    """Conserver tous les bilans passés, y compris le tout premier résultat."""
    page = root / "conseils/index.html"
    source_file = root / "conseils/resultats.json"
    if not page.is_file():
        return
    source = page.read_text(encoding="utf-8")
    marker = "<!-- VM_BILAN_VEILLE -->"
    if marker not in source:
        raise ValueError("Emplacement de bilan manquant")
    data = json.loads(source_file.read_text(encoding="utf-8")) if source_file.exists() else {}
    today = dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo("Europe/Paris")).date()
    records = []
    for item in data.get("bilans", []) if isinstance(data, dict) else []:
        if not isinstance(item, dict):
            continue
        try:
            day = dt.date.fromisoformat(str(item.get("date", "")))
        except ValueError:
            continue
        if day < today:
            records.append((day, item))
    records.sort(key=lambda pair: pair[0], reverse=True)
    cards = []
    days = {}
    month_names = ('janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                   'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre')
    source_hosts = {"www.uefa.com", "www.teamfrancebasket.fr", "www.teamfrancebasket.com", "scottishrugby.org", "www.beinsports.com", "www.bebasket.fr",
                    "www.estrepublicain.fr", "www.nba.com", "www.nhl.com"}
    for day, item in records:
        title = escape(str(item.get("titre", "Bilan du jour")))
        status = escape(str(item.get("statut", "En cours de vérification")))
        scope = "VIP" if item.get("type") == "vip" else "Public"
        links = []
        sources = item.get("sources", [])
        for entry in sources if isinstance(sources, list) else []:
            if not isinstance(entry, dict):
                continue
            url = str(entry.get("url", ""))
            parsed = urlparse(url)
            if parsed.scheme == "https" and parsed.hostname in source_hosts and not parsed.username and not parsed.password:
                links.append('<a href="' + escape(url, quote=True) + '" target="_blank" rel="noopener noreferrer">' + escape(str(entry.get("nom", "Source"))) + '</a>')
        content = []
        for key, cls in (("score_confirme_par_capture", "bd-score"), ("autre_selection", ""), ("note", "bd-note")):
            value = str(item.get(key, ""))
            if value:
                content.append('<p class="' + cls + '">' + escape(value).replace("\n", "<br>") + '</p>')
        figures = []
        affiche = item.get("support_visuel") == "affiche"
        etiquette_image = "l’affiche du bilan" if affiche else "la capture originale"
        texte_agrandir = "Agrandir l’affiche ↗" if affiche else "Agrandir l’original ↗"
        captures = item.get("captures", [])
        for image in captures if isinstance(captures, list) else []:
            if not isinstance(image, dict):
                continue
            filename = str(image.get("fichier", ""))
            if not re.fullmatch(r"[a-z0-9-]+\.jpg", filename):
                raise ValueError("Nom de capture de résultat invalide")
            image_path = root / "conseils/preuves" / filename
            if not image_path.is_file() or not image_path.read_bytes().startswith(b"\xff\xd8\xff"):
                raise ValueError("Capture originale de résultat manquante : " + filename)
            url = "/conseils/preuves/" + filename
            caption = escape(str(image.get("legende", "Capture fournie par la rédaction")))
            identifier = str(image.get("id", ""))
            if not re.fullmatch(r"[a-z0-9-]+", identifier):
                raise ValueError("Identifiant de capture invalide")
            width, height = int(image.get("largeur", 0)), int(image.get("hauteur", 0))
            if not (1 <= width <= 10000 and 1 <= height <= 10000):
                raise ValueError("Dimensions de capture invalides")
            figures.append(
                '<figure id="' + identifier + '"><a href="' + url + '" target="_blank" rel="noopener noreferrer" aria-label="Ouvrir ' + etiquette_image + ' : ' + caption + '">'
                + '<img src="' + url + '" width="' + str(width) + '" height="' + str(height) + '" loading="lazy" decoding="async" alt="' + caption + '"></a>'
                + '<figcaption>' + caption + '<br><a href="' + url + '" target="_blank" rel="noopener noreferrer">' + texte_agrandir + '</a></figcaption></figure>'
            )
        card = (
            '<article class="card bd-bilan" data-bilan-date="' + day.isoformat() + '">'
            + '<span class="bd-etiquette">' + day.strftime("%d/%m/%Y") + ' · ' + scope + '</span>'
            + '<h3>' + title + '</h3><p><strong>' + status + '</strong></p>'
            + ('<details class="results-evidence"><summary>🖼️ ' + ('Voir les ' + str(len(figures)) + ' captures originales' if len(figures) > 1 else 'Voir ' + etiquette_image) + '</summary><div class="result-captures">' + ''.join(figures) + '</div></details>' if figures else '')
            + ''.join(content)
            + ('<p class="bd-note">Sources : ' + ' · '.join(links) + '</p>' if links else '')
            + '<p class="bd-note">Résultats passés, sans garantie pour la suite · 18+ · Jouer comporte des risques.</p></article>'
        )
        days.setdefault(day, []).append((scope, status, card))
    months = {}
    for day, entries in days.items():
        label = str(day.day) + ' ' + month_names[day.month - 1]
        summaries = []
        for scope, status, _ in entries:
            ratio = re.match(r"(\d+) conseils? réussis? sur (\d+)", status)
            short = ratio.group(1) + '/' + ratio.group(2) if ratio else status.split(' — ')[0]
            summaries.append(scope + ' : ' + short)
        overview = ' · '.join(summaries)
        day_html = (
            '<details class="results-day" name="vm-results-day" id="resultats-' + day.isoformat() + '">'
            + '<summary><strong>' + label + '</strong><span>' + overview + '</span></summary>'
            + '<div class="results-day-content">' + ''.join(card for _, _, card in entries) + '</div></details>'
        )
        months.setdefault((day.year, day.month), []).append(day_html)
    for (year, month), entries in months.items():
        label = month_names[month - 1].capitalize() + ' ' + str(year)
        cards.append(
            '<details class="results-month" name="vm-results-month"><summary>' + label
            + '<span>' + str(len(entries)) + (' journées archivées' if len(entries) > 1 else ' journée archivée') + '</span></summary>'
            + '<div class="results-month-content">' + ''.join(entries) + '</div></details>'
        )
    section = (
        '<details id="historique-resultats" class="results-fold">'
        + '<summary>🔞 Résultats transparents · 18+ <span>Réussites et échecs · Captures originales · Archives par mois</span></summary>'
        + '<div class="results-content"><p class="results-intro">Choisis un mois, puis une date. '
        + 'Les images s’ouvrent uniquement à la demande. Le premier bilan et les échecs sont conservés.</p>'
        + _cumul_conseils(records) + ''.join(cards) + '</div></details>'
    ) if cards else ''
    source = source.replace("<!-- VM_RENDEMENT_PUBLIC -->", _resume_public_conseils(records))
    page.write_text(source.replace(marker, section), encoding="utf-8")

LIMITE_PAGES = 25 * 1024 * 1024  # Cloudflare Pages refuse tout fichier plus gros.


def _alleger_editorial_status(root):
    """Retire de l'historique publié les listes « confirmed » répétées.

    La liste du haut garde déjà les 500 dernières publications confirmées ;
    les 300 copies de l'historique la dupliquaient et faisaient dépasser 25 Mo.
    Le fichier du dépôt n'est pas modifié, seule la copie publiée est allégée.
    """
    path = root/'studio/editorial-status.json'
    if not path.exists():
        return
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except ValueError:
        return
    if isinstance(data, dict) and isinstance(data.get('history'), list):
        data['history'] = [{k: v for k, v in event.items() if k != 'confirmed'}
                           for event in data['history'] if isinstance(event, dict)]
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')


def _retirer_fichiers_trop_gros(root):
    """Dernier filet : un fichier de plus de 25 Mo bloquerait toute la mise en ligne."""
    for path in sorted(root.rglob('*')):
        if path.is_file() and path.stat().st_size > LIMITE_PAGES:
            print(f'Attention : {path.relative_to(root)} dépasse 25 Mo, retiré de la copie publiée.')
            path.unlink()


def _liens_publications_meta(root, html):
    source = root / "assets/reseaux-publications.json"
    if not source.is_file():
        return html
    liens = json.loads(source.read_text(encoding="utf-8"))

    def ajouter(m):
        balise, cible = m[0], m[1]
        actif = liens.get(cible, {})
        url = actif.get("url", "")
        adresse = urlparse(url)
        if adresse.scheme != "https" or adresse.username or adresse.password:
            return balise
        if cible.endswith("/facebook"):
            valide = adresse.netloc in ("www.facebook.com", "m.facebook.com") and re.fullmatch(
                r"/[^/]+/(?:posts|videos)/[^/]+/?|/reel/[0-9]+/?", adresse.path)
        else:
            valide = adresse.netloc == "www.instagram.com" and re.fullmatch(r"/(?:p|reel|tv)/[a-zA-Z0-9_-]+/?", adresse.path)
        if not valide:
            return balise
        nouveau = escape(url, quote=True)
        return re.sub(r'href="[^"]+"', lambda _: 'href="' + nouveau + '"', balise, count=1)

    return re.sub(r'<a\b[^>]*\bdata-publication-meta="([^"]+)"[^>]*>', ajouter, html)


RELATED_BLOCK = re.compile(r'(<h2>À lire aussi</h2>\s*)?<div class="rel">(.*?)</div>', re.DOTALL)
RELATED_LINK = re.compile(r'<a href="(/a/[A-Za-z0-9_-]+\.html)"[^>]*>.*?</a>', re.DOTALL)


def nettoyer_articles_associes(text, routes):
    """Masquer les références historiques aux articles qui ne sont plus publiés."""
    total = 0

    def filtrer(bloc):
        nonlocal total

        def garder(lien):
            nonlocal total
            if lien[1] in routes:
                return lien[0]
            total += 1
            return ""

        contenu = RELATED_LINK.sub(garder, bloc[2])
        return (bloc[1] or "") + '<div class="rel">' + contenu + '</div>' if contenu.strip() else ""

    return RELATED_BLOCK.sub(filtrer, text), total


def _prepare_scores_snapshot(root):
    source = "https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/scores-live/scores.json"
    target = root / "scores.json"

    def checked(data):
        stamp = data.get("verifie") or data.get("maj")
        value = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        return value.timestamp() if value.tzinfo is not None else 0.0

    try:
        with urlopen(source, timeout=8) as response:
            payload = response.read(2_000_001)
        if len(payload) > 2_000_000:
            raise ValueError("taille inattendue")
        snapshot = json.loads(payload)
        when = checked(snapshot)
        if not isinstance(snapshot.get("matchs"), list) or not 0 < when <= dt.datetime.now(dt.timezone.utc).timestamp() + 60:
            raise ValueError("horodatage ou liste invalide")
        try:
            previous = checked(json.loads(target.read_bytes()))
        except (OSError, ValueError, TypeError, AttributeError):
            previous = 0.0
        if when > previous:
            target.write_bytes(payload)
            print(f"Instantané des scores prêt ({len(snapshot['matchs'])} matchs).")
    except (OSError, ValueError, TypeError, AttributeError):
        print("Instantané des scores indisponible : les données présentes sont conservées.")


def _canonicaliser_metadonnees_breve(text, path):
    """Aligner les métadonnées des anciennes brèves sur l’URL Cloudflare."""
    if path.name == 'index.html' or 'noindex' in text[:600]:
        return text
    head, separator, body = text.partition('</head>')
    if not separator:
        return text
    archive_url = 'https://velocemercato.fr/a/' + path.name
    public_url = archive_url.removesuffix('.html')
    # L’URL de cette page est utilisée dans canonical, og:url et NewsArticle.
    head = head.replace(f'"{archive_url}"', f'"{public_url}"')
    head = head.replace(f"'{archive_url}'", f"'{public_url}'")
    return head + separator + body


def _canonicaliser_sitemap(root):
    path = root / 'sitemap.xml'
    if not path.is_file():
        return
    xml = path.read_text(encoding='utf-8')
    xml = re.sub(r'(<loc>https://velocemercato\.fr/a/[a-zA-Z0-9_-]+)\.html(</loc>)',
                 r'\1\2', xml)
    noindex = r'(?:/vm/|/mentions-legales(?:\.html)?|/politique-de-confidentialite(?:\.html)?)'
    xml = re.sub(r'[ \t]*<url>\s*<loc>https://velocemercato\.fr' + noindex +
                 r'</loc>(?:(?!</url>).)*</url>[ \t]*\n?', '', xml, flags=re.S)
    path.write_text(xml, encoding='utf-8')


def prepare(root):
    _canonicaliser_sitemap(root)
    _prepare_scores_snapshot(root)
    _alleger_editorial_status(root)
    _retirer_fichiers_trop_gros(root)
    _prepare_affiches(root)
    _prepare_bilan_veille(root)
    from tools.reseaux_bureau import preparer_fils_bureau
    preparer_fils_bureau(root)
    count = liens_retires = 0
    articles = {"/a/" + p.name for p in (root / "a").glob("*.html") if p.is_file()}
    for path in sorted(root.rglob('*.html')):
        relative = path.relative_to(root)
        if relative.parts[0] == 'en' or any(part in {'.github', 'tests', 'tools', 'docs'} for part in relative.parts):
            continue
        text = path.read_text(encoding='utf-8')
        if relative.parts[0] == 'a' and len(relative.parts) == 2:
            text = _canonicaliser_metadonnees_breve(text, path)
            if 'class="rel"' in text:
                text, retires = nettoyer_articles_associes(text, articles)
                liens_retires += retires
        if path == root/'index.html':
            text = _liens_publications_meta(root, text)
        if path == root/'foot/index.html':
            articles = json.loads((root/'articles.json').read_text(encoding='utf-8'))
            rows = sorted((a for a in articles if isinstance(a, dict) and a.get('titre') and a.get('id')),
                          key=lambda a: str(a.get('publishedAt', '')), reverse=True)[:4]
            items = []
            for article in rows:
                source = next((s.get('nom') for s in article.get('sources', []) if s.get('nom')), 'Source citée')
                ident = re.sub(r'[^a-zA-Z0-9_-]', '', str(article['id']))
                items.append('<li><a href="/a/'+ident+'.html">'+escape(article['titre'])+'</a><small>'+
                             escape(str(article.get('publishedAt', ''))+' · '+source)+'</small><p>'+
                             escape(str(article.get('resume', '')))+'</p></li>')
            snapshot = '<section id="actualites-du-jour" aria-label="Dernières actualités football sourcées"><h3>Les dernières actualités foot</h3><ul>'+''.join(items)+'</ul><a href="#feed-title">Voir toutes les actualités mises à jour</a></section>'
            text = re.sub(r'(<!-- VM_ACTUS_VISIBLES_START -->)(?s:.*?)(<!-- VM_ACTUS_VISIBLES_END -->)',
                          lambda match: match[1]+snapshot+match[2], text, count=1)
        parser = RemoveNavigation('multisport' in path.relative_to(root).parts)
        parser.feed(text)
        if parser.depth:
            raise ValueError(f'Bloc de navigation non fermé dans {path.relative_to(root)}')
        text = ''.join(parser.output)
        css = '<link rel="stylesheet" href="/assets/vm-lecture.css?v=20261111b">'
        if '/assets/vm-lecture.css' not in text:
            text = text.replace('</head>', css + '\n</head>', 1)
        if 'multisport/univers.js' in text or 'assets/accueil-rubriques.js' in text:
            if '/assets/multisport-pertinence.js' not in text:
                text = text.replace('</head>', '<script src="/assets/multisport-pertinence.js"></script>\n</head>', 1)
        if path != root/'index.html' and 'class="vm-retour-accueil"' not in text:
            text = re.sub(r'(<body\b[^>]*>)', r'\1<a class="vm-retour-accueil" href="/">← Accueil</a>', text, count=1)
        for asset in ('assets/broadcast-feed.js', 'assets/accueil-rubriques.js', 'multisport/univers.js'):
            text = re.sub(r'(src=[\"\']/?' + re.escape(asset) + r')(?:\?[^\"\']*)?([\"\'])', r'\1?v=20261111b\2', text)
        path.write_text(text, encoding='utf-8')
        count += 1
    print(f'{count} pages préparées avec leur accès à l’accueil et leur style de lecture.')


if __name__ == '__main__':
    prepare(Path(sys.argv[1]).resolve())

