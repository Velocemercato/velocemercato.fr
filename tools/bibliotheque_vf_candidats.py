#!/usr/bin/env python3
"""Construit bibliotheque-vf/candidats.json à partir de l'inventaire du dossier ChatGPT.

Chaque titre reste un CANDIDAT : aucune disponibilité, aucune VF ni aucun lien n'est inventé.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "docs" / "DOSSIER_BIBLIOTHEQUE_VF.md"
SORTIE = ROOT / "bibliotheque-vf" / "candidats.json"
SECTIONS = {
    "Dessins animés français/européens": ("dessin_anime", "France/Europe"),
    "Dessins animés internationaux": ("dessin_anime", "International"),
    "Anime japonais": ("anime", "Japon"),
    "Séries nostalgiques et françaises": ("serie", "France/International"),
    "Séries internationales": ("serie", "International"),
    "Films d'animation": ("film_animation", "International"),
    "Films de fiction et films pour public majeur": ("film", "International"),
}
CHAMPS_VIDES = ("titre_original", "annee", "classification_fr", "saison", "episode", "diffuseur",
                "url_officielle", "embed_autorise", "gratuit", "accessible_france", "droits_verifies",
                "date_verification", "preuve_source")


def slug(texte):
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def construire(texte):
    oeuvres, vus, section = [], set(), None
    for ligne in texte.splitlines():
        if ligne.startswith("### "):
            section = SECTIONS.get(ligne[4:].strip())
            continue
        if ligne.startswith("#"):
            section = None
            continue
        if not section or not ligne.strip():
            continue
        corps = re.sub(r"\.\s*Classifications.*$", "", ligne.strip())
        for brut in corps.split(" ; "):
            titre = brut.strip().rstrip(".")
            adulte = "[adulte]" in titre
            titre = titre.replace("[adulte]", "").strip()
            ident = slug(titre)
            if not titre or ident in vus:
                continue
            vus.add(ident)
            oeuvre = {"id": ident, "titre_fr": titre, "type": section[0], "pays": section[1],
                      "public": "adulte" if adulte else ("a_verifier" if section[0] == "film" else "tous"),
                      "audio": "VF_A_VERIFIER", "qualite": "inconnue", "lien_type": "INDISPONIBLE",
                      "statut": "candidat"}
            oeuvre.update({c: None for c in CHAMPS_VIDES})
            oeuvres.append(oeuvre)
    return oeuvres


def main():
    oeuvres = construire(DOSSIER.read_text(encoding="utf-8"))
    SORTIE.write_text(json.dumps({
        "_note": "Inventaire de CANDIDATS (dossier du 04/11/2026). Rien n'est vérifié ici : "
                 "audio, diffuseur, droits et accès restent à prouver lien par lien (voir liens.json).",
        "total": len(oeuvres), "oeuvres": oeuvres}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(oeuvres)} candidats écrits dans {SORTIE.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
