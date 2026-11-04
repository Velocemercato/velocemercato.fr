#!/usr/bin/env python3
"""Bibliothèque VF : contrôle quotidien des liens YouTube officiels (lecture seule).

Pour chaque lien de bibliotheque-vf/liens.json :
  - oEmbed YouTube : la vidéo existe-t-elle, l'intégration est-elle autorisée, qui la publie ?
  - page publique de la vidéo (hl=fr, gl=FR) : chaîne exacte (channelId), pays autorisés,
    durée, qualité maximale, pistes audio, statut de lecture.
Résultat : bibliotheque-vf/verifications.json, avec la date et les preuves.

Règles :
  - « VF_CONFIRME » seulement si une piste audio française est déclarée par YouTube, ou si la
    CHAÎNE OFFICIELLE PROUVÉE annonce explicitement la VF / le français dans le titre.
    Un titre en français ne suffit pas (VOSTFR possible).
  - « verifie » = chaîne officielle prouvée + vidéo lisible + France autorisée + VF confirmée.
    Ou si la chaîne officielle, prouvée par son identifiant, est l'édition française déclarée
    (« francophone » dans liens.json, avec la page de la chaîne en preuve).
  - Aucun téléchargement de vidéo : seules les métadonnées publiques sont lues.
"""
import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIENS = ROOT / "bibliotheque-vf" / "liens.json"
SORTIE = ROOT / "bibliotheque-vf" / "verifications.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
MARQUEUR_VF = re.compile(r"(?<![A-Za-z])VF(?![A-Za-z])|version fran[cç]aise|en fran[cç]ais|\bfran[cç]ais\b|🇫🇷", re.I)
MARQUEUR_VO = re.compile(r"VOSTFR|VOST\b|sous-titr", re.I)


def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Language": "fr-FR,fr;q=0.9",
        "Cookie": "CONSENT=YES+cb; SOCS=CAI"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, ""


def oembed(video, get=http_get):
    watch = "https://www.youtube.com/watch?v=" + video
    code, body = get("https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(watch, safe=""))
    data = {}
    if code == 200:
        try:
            data = json.loads(body)
        except ValueError:
            data = {}
    return code, data


def extraire_player(html):
    """Extrait ytInitialPlayerResponse de la page publique (sans exécuter de script)."""
    m = re.search(r"ytInitialPlayerResponse\s*=\s*", html)
    if not m:
        return {}
    try:
        data, _ = json.JSONDecoder().raw_decode(html[m.end():])
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}


def analyser_player(player):
    details = player.get("videoDetails") or {}
    micro = (player.get("microformat") or {}).get("playerMicroformatRenderer") or {}
    jouable = (player.get("playabilityStatus") or {}).get("status")
    formats = (player.get("streamingData") or {}).get("adaptiveFormats") or []
    hauteurs = [f.get("height") for f in formats if isinstance(f.get("height"), int)]
    pistes = sorted({(f.get("audioTrack") or {}).get("id", "") for f in formats if f.get("audioTrack")} - {""})
    pays = micro.get("availableCountries")
    return {
        "channel_id": details.get("channelId") or micro.get("externalChannelId"),
        "auteur": details.get("author") or micro.get("ownerChannelName"),
        "profil": micro.get("ownerProfileUrl"),
        "titre": details.get("title"),
        "description": (details.get("shortDescription") or "")[:600],
        "duree_s": int(details["lengthSeconds"]) if str(details.get("lengthSeconds", "")).isdigit() else None,
        "jouable": jouable,
        "accessible_france": (("FR" in pays) if isinstance(pays, list) and pays else None),
        "famille": micro.get("isFamilySafe"),
        "date_mise_en_ligne": micro.get("uploadDate") or micro.get("publishDate"),
        "qualite_max": max(hauteurs) if hauteurs else None,
        "pistes_audio": pistes,
    }


def qualite(h):
    if not h:
        return "inconnue"
    return "1080p" if h >= 1080 else "720p" if h >= 720 else "SD"


def chaine_prouvee(chaine, page, oe):
    """Preuve forte : channelId ou handle attendu. Preuve faible : nom de la chaîne."""
    ids = set(chaine.get("ids") or [])
    handles = {h.lower() for h in chaine.get("handles") or []}
    if page.get("channel_id") and page["channel_id"] in ids:
        return "id"
    profil = str(page.get("profil") or oe.get("author_url") or "").lower()
    if any(profil.endswith("/" + h) for h in handles):
        return "handle"
    auteur = str(page.get("auteur") or oe.get("author_name") or "")
    if any(n and n.lower() in auteur.lower() for n in chaine.get("noms") or []):
        return "nom"
    return None


def audio_vf(page, titre_oembed, preuve_chaine, chaine_francophone=False):
    pistes = page.get("pistes_audio") or []
    if any(p.lower().startswith("fr") for p in pistes):
        return "VF_CONFIRME", "piste audio française déclarée par YouTube (" + ", ".join(pistes) + ")"
    texte = " ".join(filter(None, [titre_oembed, page.get("titre"), page.get("description")]))
    if MARQUEUR_VO.search(texte):
        return "PAS_DE_VF", "la publication annonce une version sous-titrée"
    if preuve_chaine in ("id", "handle") and MARQUEUR_VF.search(" ".join(filter(None, [titre_oembed, page.get("titre")]))):
        return "VF_CONFIRME", "VF / français annoncé dans le titre par la chaîne officielle prouvée"
    if preuve_chaine in ("id", "handle") and chaine_francophone:
        return "VF_CONFIRME", "chaîne officielle francophone prouvée par son identifiant (édition française)"
    return "VF_A_VERIFIER", "aucune preuve automatique de l'audio français : écoute humaine requise"


def verifier(lien, chaines, get=http_get, maintenant=None):
    maintenant = maintenant or dt.datetime.now(dt.timezone.utc)
    video = str(lien.get("video") or "")
    res = {"id": lien.get("id"), "oeuvre": lien.get("oeuvre"), "titre_vm": lien.get("titre"),
           "statut_catalogue": lien.get("statut"), "page_vm": lien.get("page"),
           "url_officielle": "https://www.youtube.com/watch?v=" + video, "diffuseur": "YouTube",
           "date_verification": maintenant.isoformat(timespec="seconds")}
    if not VIDEO_ID.fullmatch(video):
        res.update(statut="retire", lien_type="INDISPONIBLE", motif="identifiant vidéo invalide")
        return res
    code, oe = oembed(video, get)
    res["oembed_http"] = code
    status, html = get("https://www.youtube.com/watch?v=" + video + "&hl=fr&gl=FR")
    page = analyser_player(extraire_player(html)) if status == 200 else {}
    chaine = chaines.get(lien.get("chaine")) or {}
    preuve = chaine_prouvee(chaine, page, oe)
    audio, motif_audio = audio_vf(page, oe.get("title"), preuve, chaine.get("francophone") is True)
    embed = True if code == 200 else False if code in (401, 403) else None
    existe = code in (200, 401, 403) or page.get("jouable") == "OK"
    res.update({
        "titre_youtube": oe.get("title") or page.get("titre"),
        "chaine_youtube": oe.get("author_name") or page.get("auteur"),
        "chaine_url": oe.get("author_url") or page.get("profil"),
        "channel_id": page.get("channel_id"),
        "chaine_attendue": chaine.get("nom"),
        "preuve_chaine": preuve,
        "audio": audio, "preuve_audio": motif_audio,
        "pistes_audio": page.get("pistes_audio") or [],
        "qualite": qualite(page.get("qualite_max")),
        "duree_s": page.get("duree_s"),
        "embed_autorise": embed,
        "gratuit": True if existe else None,
        "accessible_france": page.get("accessible_france"),
        "jouable": page.get("jouable"),
        "famille": page.get("famille"),
        "lien_type": ("LECTEUR_OFFICIEL" if embed else "LIEN_DIFFUSEUR") if existe else "INDISPONIBLE",
    })
    if code == 0 and status == 0:
        res.update(statut="non_controle", motif="YouTube injoignable : aucun changement, nouvel essai demain")
    elif not existe:
        res.update(statut="retire", motif="vidéo introuvable ou supprimée (oEmbed " + str(code) + ")")
    elif preuve not in ("id", "handle", "nom"):
        res.update(statut="candidat", motif="chaîne officielle non prouvée")
    elif audio != "VF_CONFIRME":
        res.update(statut="candidat", motif=motif_audio)
    elif res["accessible_france"] is not True:
        res.update(statut="candidat", motif="accès depuis la France non prouvé par la page publique")
    elif preuve == "nom":
        res.update(statut="candidat", motif="chaîne reconnue par son nom seulement : ajouter son identifiant")
    else:
        res.update(statut="verifie", motif="chaîne, lecture, France et VF prouvées")
    if lien.get("statut") == "publie":
        res["alerte"] = None if res["statut"] != "retire" else "PAGE EN LIGNE À RETIRER : " + res["motif"]
    res["droits_verifies"] = preuve in ("id", "handle")
    return res


def tableau(resultats):
    lignes = ["| Lien | Catalogue | Résultat | Chaîne YouTube (preuve) | Audio | France | Intégration | Qualité | Motif |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in resultats:
        lignes.append("| {id} | {cat} | **{st}** | {ch} ({pr}) | {au} | {fr} | {em} | {q} | {mo} |".format(
            id=r["id"], cat=r["statut_catalogue"], st=r["statut"], ch=r.get("chaine_youtube") or "?",
            pr=r.get("preuve_chaine") or "aucune", au=r.get("audio", "?"),
            fr={True: "oui", False: "non", None: "?"}[r.get("accessible_france")],
            em={True: "oui", False: "non", None: "?"}[r.get("embed_autorise")],
            q=r.get("qualite", "?"), mo=str(r.get("motif", "")).replace("|", "/")))
    return "\n".join(lignes)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ecrire", action="store_true", help="écrire verifications.json")
    parser.add_argument("--pause", type=float, default=1.0, help="secondes entre deux vidéos (quotas)")
    args = parser.parse_args(argv)
    data = json.loads(LIENS.read_text(encoding="utf-8"))
    resultats = []
    for lien in data["liens"]:
        resultats.append(verifier(lien, data["chaines"]))
        time.sleep(args.pause)
    bilan = {k: sum(1 for r in resultats if r["statut"] == k) for k in ("verifie", "candidat", "retire", "non_controle")}
    bilan["publies_en_ligne"] = sum(1 for r in resultats if r["statut_catalogue"] == "publie")
    sortie = {"_note": "Généré par tools/verifier_vf.py. Lecture seule des métadonnées publiques YouTube.",
              "date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
              "bilan": bilan, "resultats": resultats}
    print(tableau(resultats))
    print("\nBilan : " + json.dumps(bilan, ensure_ascii=False))
    for r in resultats:
        if r.get("alerte"):
            print("::warning::" + r["id"] + " — " + r["alerte"])
    if args.ecrire:
        SORTIE.write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
