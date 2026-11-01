#!/usr/bin/env python3
"""Rapport en lecture seule des publications Facebook et Instagram du jour.

INTERDICTIONS : aucun POST, DELETE, commit, sauvegarde d'état ni réinitialisation.
Ne renvoie que les liens publics déjà publiés, après contrôle de la destination.
Dates en heure de Paris ; aucune fuite de jetons ou messages bruts.
"""
import datetime as dt
import os
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError
from tools.publier_meta import Graph, ensure_meta_targets

PARIS = ZoneInfo("Europe/Paris")
DAY = dt.datetime.now(PARIS).date()
PAGE_IDS = {
    "meta": "1384363904759072",
    "meta_univers": "1349998758205153",
    "meta_pronos": "112294796981981",
}


def parsed(value):
    t = dt.datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("Horodatage sans zone horaire")
    return t.astimezone(PARIS)


def graph_page(graph, account, data):
    page_id = PAGE_IDS[account]
    token = data.get("page_token")
    results, after = [], None
    for idx in range(3):
        args = {
            "fields": "id,created_time,from{id},permalink_url",
            "limit": 100, "access_token": token,
        }
        if after:
            args["after"] = after
        output = graph.call("GET", page_id + "/published_posts", args)
        items = output.get("data") or []
        if not isinstance(items, list):
            raise DeliveryError("Données Meta incomplètes")
        found_older = False
        for p in items:
            try:
                stamp = parsed(p.get("created_time"))
            except (ValueError, TypeError):
                continue
            if stamp.date() < DAY:
                found_older = True
                continue
            if stamp.date() != DAY:
                continue
            ident = str(p.get("id") or "")
            if not re.fullmatch(re.escape(page_id) + r"_[0-9]+", ident):
                continue
            author = str((p.get("from") or {}).get("id") or "")
            if author != page_id:
                # Vérification supplémentaire par ID, en lecture seule.
                check = graph.call("GET", ident, {
                    "fields": "id,from{id},permalink_url",
                    "access_token": token})
                if str(check.get("id") or "") != ident:
                    continue
                if str((check.get("from") or {}).get("id") or "") != page_id:
                    continue
                if not p.get("permalink_url"):
                    p = {**p, "permalink_url": check.get("permalink_url")}
            url = str(p.get("permalink_url") or "")
            if not (url.startswith("https://www.facebook.com/")
                    or url.startswith("https://m.facebook.com/")):
                continue
            results.append((stamp, ident, url))
        paging = output.get("paging") or {}
        if found_older or not paging.get("next"):
            return results
        new_after = (paging.get("cursors") or {}).get("after")
        if not new_after or new_after == after:
            raise DeliveryError("Pagination de la Page incomplète")
        after = new_after
    print("::warning::Facebook " + account + " : pagination tronquée à 300 posts")
    return results


def graph_instagram(graph, account, data):
    if account == "meta_pronos":
        return []
    ig = str(data.get("ig_id") or "")
    if not ig.isdecimal():
        return []
    token = data.get("page_token")
    result = graph.call("GET", ig + "/media", {
        "fields": "id,timestamp,permalink,media_type",
        "limit": 100, "access_token": token,
    })
    rows = []
    for m in result.get("data") or []:
        try:
            stamp = parsed(m.get("timestamp"))
        except (ValueError, TypeError):
            continue
        if stamp.date() != DAY:
            continue
        ident = str(m.get("id") or "")
        url = str(m.get("permalink") or "")
        if ident.isdecimal() and url.startswith("https://www.instagram.com/"):
            rows.append((stamp, ident, url))
    return rows


def main():
    folder = Path(os.environ["RUNNER_TEMP"]) / "vm-broadcast-state"
    state = State(folder / "state.enc", os.getenv("VM_DIFFUSION_STATE_KEY", ""))
    ensure_meta_targets(state)  # Même contrôle de sécurité que le correctif.
    graph = Graph()
    count = 0
    print("::notice::AUDIT PUBLICATIONS REELLES " + DAY.isoformat() + ", LECTURE SEULE")
    for account in ("meta", "meta_univers", "meta_pronos"):
        data = (state.data.get("tokens") or {}).get(account) or {}
        if not data:
            print("::warning::" + account + " : compte non connecté")
            continue
        for label, retrieve in (("FB", graph_page), ("IG", graph_instagram)):
            if label == "IG" and account == "meta_pronos":
                print("::notice::IG meta_pronos : INTERDIT, aucune requête Instagram")
                continue
            try:
                items = retrieve(graph, account, data)
                print("::notice::COMPTE " + label + " " + account +
                      " POSTS_CONFIRME_REPERTOIRES=" + str(len(items)))
                for stamp, ident, url in sorted(items, reverse=True):
                    print("::notice::PUBLICATION " + label + " " + account +
                          " " + stamp.strftime("%Y-%m-%d %H:%M") +
                          " ID=" + ident + " URL=" + url)
                    count += 1
            except (DeliveryError, OSError, ValueError, TypeError) as error:
                print("::warning::" + label + " " + account +
                      " : vérification API indisponible (" + type(error).__name__ +
                      "), ne pas déclarer de publication confirmée")
    print("::notice::AUDIT TERMINE, liens confirmés observés=" + str(count) +
          ", ZERO suppression, ZERO diffusion.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("::error::Rapport non exécutable, sans diffusion (" + type(error).__name__ + ")")
        sys.exit(1)
