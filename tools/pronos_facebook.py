#!/usr/bin/env python3
"""Troisième destination Facebook : RQ Pronos. Isolée de meta et meta_univers.

Par défaut : diagnostic sans publication. Un seul test explicite est autorisé,
puis validation ID/URL par l'API Meta. Aucune liaison Instagram.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save
from tools.publier_meta import Graph

PARIS = ZoneInfo("Europe/Paris")
UTC = dt.timezone.utc
PAGE_VAR = "VM_FACEBOOK_PRONOS_PAGE_ID"
RISK = "Jouer comporte des risques, 18+, Joueurs Info Service 09 74 75 13 13"
VALID_POST = re.compile(r"^[0-9]+_[0-9]+$")
VALID_URL = re.compile(r"^https://(?:www\.|m\.)?facebook\.com/[^\s]+$")


def load(path, default):
    p = ROOT / path
    if not p.is_file():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def normal(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def recent(date_string, now, hours=24):
    try:
        timestamp = dt.datetime.fromisoformat(str(date_string).replace("Z", "+00:00"))
        return timestamp.tzinfo is not None and dt.timedelta(0) <= now - timestamp <= dt.timedelta(hours=hours)
    except (ValueError, TypeError):
        return False


def page_access(state):
    wanted = os.getenv(PAGE_VAR, "").strip()
    if not re.fullmatch(r"[0-9]{5,25}", wanted):
        raise DeliveryError(PAGE_VAR + " manquant ou invalide.")
    meta = state.data.get("tokens", {}).get("meta_pronos") or {}
    if str(meta.get("page_id") or "") != wanted or not meta.get("page_token"):
        raise DeliveryError("RQ Pronos non autorisée : lancer connecter-meta.yml en mode pronos.")
    if meta.get("ig_id") or meta.get("ig_username"):
        raise DeliveryError("RQ Pronos doit être Facebook uniquement.")
    other = state.data.get("tokens", {})
    for key in ("meta", "meta_univers"):
        if str((other.get(key) or {}).get("page_id") or "") == wanted:
            raise DeliveryError("L'ID RQ Pronos est déjà utilisé par " + key + " : refus.")
    return meta


def propose(now):
    """Au plus un contenu par créneau ; textes originaux, sans dupliquer les posts de VeloceMercato."""
    local = now.astimezone(PARIS)
    hour = local.hour
    items = []
    if 7 <= hour < 12:
        univers, file = "foot", "articles.json"
    elif 12 <= hour < 15:
        univers, file = "belfort", "belfort/actus.json"
    elif 15 <= hour < 18:
        univers, file = "gaming", "vm-gaming/news.json"
    elif 18 <= hour < 20:
        univers, file = "actus", "actus/news.json"
    elif 20 <= hour < 22:
        univers, file = "jt", "studio/diffusions.json"
    else:
        univers, file = "projet", None
    if univers == "projet":
        # Un projet VM Univers par jour au maximum, avec texte propre à RQ Pronos.
        projects = [
            ("VM Belfort", "https://velocemercato.fr/belfort/", "L'info près de chez toi"),
            ("VM Gaming", "https://velocemercato.fr/vm-gaming/", "L'actualité jeu vidéo"),
            ("VM Univers", "https://vmunivers.fr/", "Découvre nos projets"),
            ("Véloce Mercato", "https://velocemercato.fr/", "Le foot sans les romans"),
        ]
        name, url, detail = projects[local.toordinal() % len(projects)]
        return {"key": f"projet/{local:%Y-%m-%d}", "text": f"👑 Le projet VM du jour : {name}\n\n{detail}. Découvre-le ici 👇\n{url}\n\n#VMUnivers #RQPronos", "link": url}
    if univers == "belfort":
        rows = load(file, {}).get("titres", [])
        for row in rows:
            if recent(row.get("d"), now) and row.get("t") and str(row.get("u", "")).startswith("https://"):
                if not row.get("s"):
                    continue
                return {"key": "belfort/" + re.sub(r"[^a-z0-9]", "", str(row["u"]).lower())[-70:],
                        "text": f"📍 VM Belfort : {normal(row['t'])}\n\nInformation relayée par {normal(row['s'])}. À lire et vérifier auprès de la source 👇\n{row['u']}\n\n#Belfort #FrancheComte #VMUnivers",
                        "link": row["u"]}
        return None
    if univers == "jt":
        rows = load(file, [])
        for row in rows:
            video = (row.get("plateformes") or {}).get("youtube") or {}
            if (recent(row.get("date_publication"), now, 10) and video.get("status") == "published"
                    and re.fullmatch(r"https://www\.youtube\.com/watch\?v=[\w-]{11}", str(video.get("url", "")))):
                return {"key": "jt/" + str(row.get("id")), "text": f"🎬 LE JT VM : {normal(row.get('titre'))}\n\nFootball, actu et gaming en version express : regarde l'édition et donne ton avis !\n{video['url']}\n\n#JT #VMUnivers #RQPronos", "link": video["url"]}
        return None
    rows = load(file, [])
    domain = {"foot": "https://velocemercato.fr/", "actus": "https://velocemercato.fr/actus/", "gaming": "https://velocemercato.fr/vm-gaming/"}[univers]
    for row in rows:
        if not (recent(row.get("publishedAt"), now) and row.get("titre") and row.get("resume")):
            continue
        sources = [s for s in row.get("sources", []) if s.get("nom") and str(s.get("url", "")).startswith("https://")]
        if not sources:
            continue
        # Ne pas recopier les brèves entières utilisées par les autres Pages.
        icon = {"foot": "⚽", "actus": "📰", "gaming": "🎮"}[univers]
        key = f"{univers}/{row.get('id')}"
        text = (f"{icon} À LA UNE SUR VM : {normal(row['titre'])}\n\n"
                f"Notre sélection du jour. Source : {normal(sources[0]['nom'])}.\n"
                f"Découvre l'info et rejoins la discussion 👇\n{domain}\n\n"
                f"#RQPronos #VMActus #VeloceMercato")
        return {"key": key, "text": text, "link": domain}
    return None


def prono(now):
    data = load("prono.json", {})
    if not data or not recent(data.get("date"), now, 30):
        return None
    match = normal(data.get("match"))
    avis = normal(data.get("avis"))
    if not match or not avis or not re.fullmatch(r"\d{1,2}\s*[–-]\s*\d{1,2}", str(data.get("score", ""))):
        return None
    return {"key": "prono/" + str(data.get("id", "")),
            "text": (f"⚽ LE PRONO VM — ANALYSE, PAS UNE PROMESSE\n\n{match}\n"
                     f"Notre avis sportif : {avis}\n"
                     f"Score envisagé : {data['score']} (simple hypothèse, jamais garanti).\n"
                     f"Aucune mise réelle ni montante : bankroll uniquement simulée.\n\n{RISK}\n"
                     f"Plus d'actus : https://velocemercato.fr/\n#RQPronos #Football"),
            "link": "https://velocemercato.fr/"}


def plan(now):
    """Liste des sujets admissibles, pas plus d'un pronostic du jour."""
    items = []
    item = propose(now)
    if item:
        items.append(item)
    local = now.astimezone(PARIS)
    if 17 <= local.hour < 20:
        forecast = prono(now)
        if forecast:
            items.append(forecast)
    return items


def verify(graph, token, page_id, post_id):
    if not VALID_POST.fullmatch(str(post_id)) or not str(post_id).startswith(page_id + "_"):
        raise DeliveryError("L'ID retourné ne correspond pas à RQ Pronos.")
    proof = graph.call("GET", str(post_id), {"fields": "id,permalink_url,from{id}", "access_token": token})
    if str(proof.get("id")) != str(post_id) or str((proof.get("from") or {}).get("id")) != page_id:
        raise DeliveryError("Publication non vérifiée : ID de Page différent.")
    url = str(proof.get("permalink_url") or "")
    if not VALID_URL.fullmatch(url):
        raise DeliveryError("Publication non vérifiée : URL Facebook absente ou inattendue.")
    return url


def execute(state, graph, action, now=None):
    now = now or dt.datetime.now(UTC)
    meta = page_access(state)
    page = str(meta["page_id"])
    texts = plan(now)
    recorded = state.data.setdefault("meta_pronos_accuses", {})
    if action == "diagnostic":
        print("::notice::DIAGNOSTIC SANS PUBLICATION : Page ID " + page)
        print("::notice::Sujets prêts : " + str(len(texts)))
        for item in texts:
            print("::notice::Sujet : " + item["key"])
        return
    # Un seul post test et jamais de publication en double après interruption.
    if action != "test":
        raise DeliveryError("Action non autorisée.")
    if os.getenv("VM_PRONOS_TEST_APPROVED") != "true":
        raise DeliveryError("Test non autorisé : VM_PRONOS_TEST_APPROVED doit être true.")
    if recorded.get("test/unique"):
        raise DeliveryError("Un test a déjà été tenté. Vérifier son résultat, ne pas renvoyer.")
    if not texts:
        raise DeliveryError("Aucun sujet sourcé récent disponible : aucun post envoyé.")
    item = texts[0]
    recorded["test/unique"] = {"status": "envoi", "key": item["key"], "at": now.isoformat()}
    state.save()  # avant le contact Meta
    message = "⚽ VM ACTUS & PRONOS\n\n" + item["text"]
    response = graph.call("POST", page + "/feed",
                          {"message": message, "link": item["link"], "access_token": meta["page_token"]})
    post_id = str(response.get("id") or "")
    recorded["test/unique"] = {"status": "envoye_a_verifier", "id": post_id, "key": item["key"]}
    state.save()
    url = verify(graph, meta["page_token"], page, post_id)
    recorded["test/unique"] = {"status": "publie_confirme", "id": post_id, "url": url, "key": item["key"]}
    state.save()
    print("::notice::POST TEST CONFIRMÉ : id=" + post_id + " url=" + url)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["diagnostic", "test"])
    parser.add_argument("--state", required=True, type=Path)
    args = parser.parse_args()
    state = State(args.state, os.getenv("VM_DIFFUSION_STATE_KEY", ""),
                  lambda: git_save(args.state))
    execute(state, Graph(), args.action)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("::error::" + (str(error) if isinstance(error, DeliveryError)
                             else "Échec du test (" + type(error).__name__ + ")"))
        sys.exit(1)
