"""Exporter les permaliens publics de la diffusion VM, sans publier sur Meta."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError
from tools.editorial_vm import confirm, identity, ledger
from tools.publier_meta import Graph, ensure_meta_targets

DESTINATIONS = (
    ("meta", "facebook"), ("meta_univers", "facebook"), ("meta_pronos", "facebook"),
    ("meta", "instagram"), ("meta_univers", "instagram"),
)
RUBRIQUES = {"actus", "foot", "multisport", "gaming", "belfort", "projet"}
SORTIE = ROOT / "assets/reseaux-publications.json"


def publication(url, network):
    u = urlsplit(url or "")
    if u.scheme != "https" or u.username or u.password:
        return False
    if network == "instagram":
        return u.netloc == "www.instagram.com" and bool(re.fullmatch(r"/(?:p|reel|tv)/[\w-]+/?", u.path, re.ASCII))
    return u.netloc in ("www.facebook.com", "m.facebook.com") and bool(
        re.fullmatch(r"/[^/]+/(?:posts|videos)/[^/]+/?|/reel/[0-9]+/?", u.path))


def date_receipt(row):
    try:
        date = dt.datetime.fromisoformat(row.get("at", ""))
        return date if date.tzinfo else dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    except (ValueError, TypeError):
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc)


def recents(state, account, network):
    for cle, raw in ledger(state, account).items():
        if not isinstance(raw, dict) or raw.get("status") != "publie_confirme" or not publication(raw.get("url"), network):
            continue
        morceaux = cle.split("/")
        rubrique = None
        if len(morceaux) == 4 and morceaux[:2] == ["editorial", network] and morceaux[2] in RUBRIQUES:
            rubrique = morceaux[2]
        elif len(morceaux) == 3 and morceaux[0] == "belfort":
            if morceaux[1] == ("source" if network == "facebook" else "instagram"):
                rubrique = "belfort"
        if rubrique:
            yield {"id": str(raw.get("id") or raw.get("post") or ""), "url": raw["url"],
                   "date": date_receipt(raw), "rubrique": rubrique}


def derniere_publication(state, graph, account, network):
    meta = state.data.get("tokens", {}).get(account) or {}
    identity(graph, meta, account, network)
    for entree in sorted(recents(state, account, network), key=lambda row: row["date"], reverse=True)[:6]:
        if not entree["id"]:
            continue
        try:
            url = confirm(graph, meta, network, entree["id"])
        except DeliveryError:
            continue
        if publication(url, network):
            return {"url": url, "date": entree["date"].isoformat(), "rubrique": entree["rubrique"]}
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    state = State(args.state, os.environ.get("VM_DIFFUSION_STATE_KEY", ""))
    ensure_meta_targets(state)
    graph = Graph()
    liens = json.loads(SORTIE.read_text(encoding="utf-8"))
    for account, network in DESTINATIONS:
        cle = account + "/" + network
        try:
            row = derniere_publication(state, graph, account, network)
        except DeliveryError:
            print(cle + " : contrôle Meta indisponible, lien actuel conservé.")
            continue
        if row:
            liens[cle] = row
            print(cle + " : " + row["rubrique"] + " · " + row["date"] + " · " + row["url"])
        else:
            print(cle + " : aucune publication d'actualité confirmée, lien actuel conservé.")
    SORTIE.write_text(json.dumps(liens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
