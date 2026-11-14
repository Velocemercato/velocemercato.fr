"""Applique les demandes de navigation aux pages du site avant leur publication."""
from html.parser import HTMLParser
from pathlib import Path
import re
import json
from html import escape
import sys
import datetime as dt
import zipfile

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
    """Extraire uniquement les PNG attendus et injecter la galerie côté déploiement."""
    from tools.pronos_public import section_affiches_publiques
    config_path = root / "pronos/affiches-public.json"
    archive_path = root / "pronos/affiches/affiches-veloce-14-novembre-2026.zip"
    page = root / "pronos/index.html"
    if not (config_path.is_file() and archive_path.is_file() and page.is_file()):
        return
    data = json.loads(config_path.read_text(encoding="utf-8"))
    expected = {str(row["fichier"]) for row in data.get("affiches", []) if isinstance(row, dict) and "fichier" in row}
    if not expected or len(expected) > 4:
        return
    with zipfile.ZipFile(archive_path) as archive:
        members = {info.filename: info for info in archive.infolist()}
        for name in expected:
            if not re.fullmatch(r"[a-z0-9-]+\.png", name):
                raise ValueError("Nom d'affiche invalide")
            info = members.get(name)
            if info is None or info.file_size > 3_500_000:
                raise ValueError("PNG attendu manquant ou trop volumineux")
            data_bytes = archive.read(name)
            if not data_bytes.startswith(b"\\x89PNG\\r\\n\\x1a\\n"):
                raise ValueError("Format PNG invalide")
            target = root / "pronos/affiches" / name
            target.write_bytes(data_bytes)
    galerie = section_affiches_publiques(root, dt.datetime.now(dt.timezone.utc))
    if galerie:
        source = page.read_text(encoding="utf-8")
        if 'id="affiches-du-jour"' not in source:
            page.write_text(source.replace("<main>", "<main>" + galerie, 1), encoding="utf-8")


def prepare(root):
    _prepare_affiches(root)
    count = 0
    for path in sorted(root.rglob('*.html')):
        if any(part in {'.github', 'tests', 'tools', 'docs'} for part in path.relative_to(root).parts):
            continue
        text = path.read_text(encoding='utf-8')
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
