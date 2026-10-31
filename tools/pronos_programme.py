#!/usr/bin/env python3
"""Programme quotidien RQ Pronos : destination Facebook seule, vérification obligatoire.

AUCUNE publication sans :
  - VM_AUTO_PRONOS=true
  - le post unique "test/unique" confirmé dans l'état chiffré
  - identifiant de Page exact (VM_FACEBOOK_PRONOS_PAGE_ID)
Un seul post par créneau et jamais de doublon après erreur ou interruption.
Les 2 autres Pages et Instagram ne sont ni consultés ni modifiés.
"""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save
from tools.publier_meta import Graph
from tools.pronos_facebook import page_access, verify, normal, recent, prono, RISK

PARIS = ZoneInfo("Europe/Paris")
UTC = dt.timezone.utc
# 7-8 posts réguliers + 1 pronostic seulement s'il existe le jour concerné.
# Pas de rafale : 1 seul post par lancement, et des créneaux espacés.
SLOTS = {8: "foot", 10: "foot", 12: "belfort", 14: "gaming",
         16: "foot", 17: "prono", 18: "actus", 20: "jt", 21: "projet"}
NEWS = {
    "foot": ("articles.json", "⚽", "https://velocemercato.fr/"),
    "actus": ("actus/news.json", "📰", "https://velocemercato.fr/actus/"),
    "gaming": ("vm-gaming/news.json", "🎮", "https://velocemercato.fr/vm-gaming/"),
}
PROJETS = (
    ("VM Univers", "https://vmunivers.fr/", "Découvre tous nos projets, sites et outils"),
    ("VM Gaming", "https://velocemercato.fr/vm-gaming/", "L'actualité des jeux vidéo et de la communauté"),
    ("VM Belfort", "https://velocemercato.fr/belfort/", "Les nouvelles et bons plans près de chez nous"),
    ("Véloce Mercato", "https://velocemercato.fr/", "L'actualité foot, sans les romans"),
)


def load_json(path, default):
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def safe_url(url):
    parsed = urlparse(str(url or ""))
    return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password


def article_candidates(universe, now):
    file, icon, site = NEWS[universe]
    rows = load_json(file, [])
    if not isinstance(rows, list):
        return []
    out = []
    for a in sorted(rows, key=lambda a: str(a.get("publishedAt", "")) if isinstance(a, dict) else "", reverse=True):
        if not isinstance(a, dict) or not recent(a.get("publishedAt"), now, 30):
            continue
        ident = str(a.get("id") or "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,99}", ident):
            continue
        sources = [s for s in a.get("sources", []) if isinstance(s, dict) and s.get("nom") and safe_url(s.get("url"))]
        if not sources or not a.get("titre") or not a.get("resume"):
            continue
        src = sources[0]
        link = site
        if universe == "foot" and (ROOT / "a" / (ident + ".html")).is_file():
            link = "https://velocemercato.fr/a/" + ident + ".html"
        # Ton autonome : résumé complet mais bref, différente accroche des comptes principaux.
        headline = normal(a["titre"])[:180]
        summary = normal(a["resume"])[:330]
        content = (f"{icon} LE POINT VM — {headline}\n\n{summary}\n\n"
                   f"Info d'après {normal(src['nom'])[:75]}. "
                   f"Lire la suite et les autres actus : {link}\n\n"
                   f"#RQPronos #{'Football' if universe == 'foot' else 'VMActus' if universe == 'actus' else 'VMGaming'}")
        out.append({"key": f"{universe}/{ident}", "text": content, "link": link})
    return out


def belfort_candidates(now):
    payload = load_json("belfort/actus.json", {})
    rows = payload.get("titres", []) if isinstance(payload, dict) else []
    out = []
    for a in rows:
        if not isinstance(a, dict) or not recent(a.get("d"), now, 28):
            continue
        if not (a.get("t") and a.get("s") and safe_url(a.get("u"))):
            continue
        import hashlib
        key = hashlib.sha256(a["u"].encode("utf-8")).hexdigest()[:20]
        title = normal(a["t"])[:200]
        link = a["u"]
        out.append({"key": "belfort/" + key,
                    "text": (f"📍 VM BELFORT · LE FLASH DU COIN\n\n{title}\n\n"
                             f"Information signalée par {normal(a['s'])[:80]}. "
                             f"Retrouve les détails directement chez le média source : {link}\n\n"
                             f"Les autres informations locales : https://velocemercato.fr/belfort/\n"
                             f"#Belfort #FrancheComte #VMUnivers"),
                    "link": link})
    return out


def jt_candidates(now):
    rows = load_json("studio/diffusions.json", [])
    out = []
    for a in rows if isinstance(rows, list) else []:
        if not isinstance(a, dict) or not recent(a.get("date_publication"), now, 30):
            continue
        youtube = (a.get("plateformes") or {}).get("youtube") or {}
        url = str(youtube.get("url", ""))
        if youtube.get("status") != "published" or not re.fullmatch(r"https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}", url):
            continue
        ident = str(a.get("id", ""))
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,99}", ident):
            continue
        out.append({"key": "jt/" + ident, "link": url,
                    "text": (f"🎬 LE JT DE L'UNIVERS VM\n\n{normal(a.get('titre'))[:200]}\n\n"
                             f"Les infos importantes en vidéo. Notre émission résume l'essentiel "
                             f"du jour : regarde-la ici 👉 {url}\n\n"
                             f"Émission réalisée avec l'aide de l'IA, informations sourcées.\n"
                             f"#JT #VeloceMercato #VMActus")})
    return out


def project_candidate(now):
    local = now.astimezone(PARIS)
    name, link, description = PROJETS[local.toordinal() % len(PROJETS)]
    return {"key": f"projet/{local:%Y-%m-%d}", "link": link,
            "text": (f"👑 LE PROJET VM DU JOUR : {name}\n\n{description}. "
                     f"Notre groupe développe aussi des médias foot, des JT et des outils gratuits.\n\n"
                     f"Découvrir 👉 {link}\n\n#VMUnivers #RQPronos")}


def candidates(now, kind):
    if kind in NEWS:
        return article_candidates(kind, now)
    if kind == "belfort":
        return belfort_candidates(now)
    if kind == "jt":
        return jt_candidates(now)
    if kind == "projet":
        return [project_candidate(now)]
    if kind == "prono":
        selected = prono(now)
        return [selected] if selected else []
    return []


def publish_slot(state, graph, now=None):
    now = now or dt.datetime.now(UTC)
    if os.getenv("VM_AUTO_PRONOS") != "true":
        print("::notice::RQ Pronos désactivé : variable VM_AUTO_PRONOS différente de true.")
        return False
    account = page_access(state)
    page_id = str(account["page_id"])
    receipts = state.data.setdefault("meta_pronos_accuses", {})
    test = receipts.get("test/unique") or {}
    if test.get("status") != "publie_confirme":
        print("::notice::RQ Pronos protégé : le post test n'est pas encore confirmé. Aucun envoi.")
        return False
    if not str(test.get("id", "")).startswith(page_id + "_") or not str(test.get("url", "")).startswith("https://"):
        raise DeliveryError("Confirmation du test incohérente avec l'ID Facebook demandé.")
    local = now.astimezone(PARIS)
    # Rattraper au plus le dernier créneau manqué (moins de deux heures).
    eligible_hours = [hour for hour in SLOTS if 0 <= local.hour - hour < 2
                      and f"creneau/{local:%Y-%m-%d}/{hour:02d}" not in receipts]
    slot_hour = max(eligible_hours) if eligible_hours else local.hour
    kind = SLOTS.get(slot_hour)
    if not kind:
        print("::notice::Aucun créneau éditorial à cette heure.")
        return False
    slot = f"creneau/{local:%Y-%m-%d}/{slot_hour:02d}"
    if slot in receipts:
        print("::notice::Créneau déjà traité : aucun doublon.")
        return False
    choice = next((p for p in candidates(now, kind)
                   if isinstance(p, dict) and p.get("key") and p["key"] != test.get("key")
                   and "post/" + p["key"] not in receipts and safe_url(p.get("link"))), None)
    if not choice:
        print("::notice::Aucune information récente et sourcée pour " + kind + ". Rien n'est publié.")
        return False
    key = "post/" + choice["key"]
    def save(receipt_key, status, **extra):
        receipts[receipt_key] = {"status": status, "at": now.isoformat(timespec="seconds"), **extra}
        state.save()
    # Acquittement AVANT l'appel API pour éviter toute rediffusion après une coupure.
    save(slot, "envoi", sujet=choice["key"])
    save(key, "envoi", creneau=slot)
    response = graph.call("POST", page_id + "/feed", {
        "message": choice["text"], "link": choice["link"], "access_token": account["page_token"]})
    post_id = str(response.get("id") or "")
    save(key, "envoye_a_verifier", id=post_id, creneau=slot)
    url = verify(graph, account["page_token"], page_id, post_id)
    save(key, "publie_confirme", id=post_id, url=url, creneau=slot)
    save(slot, "publie_confirme", sujet=choice["key"], id=post_id, url=url)
    print("::notice::RQ PRONOS : POST CONFIRMÉ, ID=" + post_id + " URL=" + url)
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    args = parser.parse_args()
    state = State(args.state, os.getenv("VM_DIFFUSION_STATE_KEY", ""),
                  lambda: git_save(args.state))
    publish_slot(state, Graph())


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("::error::" + (str(error) if isinstance(error, DeliveryError)
                             else "Échec publication RQ Pronos (" + type(error).__name__ + ")"))
        sys.exit(1)
