#!/usr/bin/env python3
"""AUDIT sans suppression des publications Facebook des Pages VM autorisées.

Cibles à examiner : toutes les publications datées avant le 1er janvier 2026
(en heure de Paris). Toutes les publications de 2026 sont intouchables,
y compris janvier-octobre. Toutes les dates antérieures à 2026 sont à examiner.
Ne change aucune destination et n'effectue AUCUNE suppression.
"""
import datetime as dt
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError
from tools.publier_meta import Graph

PARIS = ZoneInfo("Europe/Paris")
CUTOFF_YEAR = 2026
PAGES = ("meta_pronos", "meta", "meta_univers")
RQ_ID = "112294796981981"
MAX_PAGES = 25
MAX_POSTS = 1800


def fetch_posts(graph, page_id, token):
    rows, cursor, seen = [], None, set()
    for _ in range(MAX_PAGES):
        params = {
            "fields": "id,created_time,permalink_url,from{id}",
            "limit": 100,
            "access_token": token,
        }
        if cursor:
            params["after"] = cursor
        result = graph.call("GET", page_id + "/published_posts", params)
        batch = result.get("data")
        if not isinstance(batch, list):
            raise DeliveryError("Réponse de publication Facebook non conforme.")
        rows.extend(batch)
        if len(rows) > MAX_POSTS:
            raise DeliveryError("Nombre trop important de publications : audit interrompu.")
        pagination = result.get("paging") or {}
        if not pagination.get("next"):
            return rows
        after = (pagination.get("cursors") or {}).get("after")
        if not after or after in seen:
            raise DeliveryError("Pagination Facebook incomplète : aucun nettoyage possible.")
        seen.add(after)
        cursor = after
    raise DeliveryError("Pagination incomplète : trop de pages de résultats.")


def classify(entries, page_id):
    candidates, safe_2026, safe_other, uncertain = [], [], [], []
    observed = set()
    for post in entries:
        ident = str(post.get("id") or "")
        if ident in observed:
            continue
        observed.add(ident)
        if not ident.startswith(page_id + "_"):
            uncertain.append(ident)
            continue
        author = str((post.get("from") or {}).get("id") or "")
        if author and author != page_id:
            uncertain.append(ident)
            continue
        try:
            time = dt.datetime.fromisoformat(
                str(post.get("created_time") or "").replace("Z", "+00:00"))
            if not time.tzinfo:
                raise ValueError("Pas de fuseau horaire")
            local = time.astimezone(PARIS)
        except (ValueError, TypeError):
            uncertain.append(ident)
            continue
        entry = (ident, local.isoformat())
        if local.year < CUTOFF_YEAR:
            candidates.append(entry)
        elif local.year >= CUTOFF_YEAR:
            safe_2026.append(entry)
        else:
            safe_other.append(entry)
    return candidates, safe_2026, safe_other, uncertain


def main():
    state_path = Path(os.environ["RUNNER_TEMP"]) / "vm-broadcast-state" / "state.enc"
    state = State(state_path, os.environ.get("VM_DIFFUSION_STATE_KEY", ""))
    connections = state.data.get("tokens") or {}
    graph = Graph()
    for account in PAGES:
        meta = connections.get(account) or {}
        page_id, token = str(meta.get("page_id") or ""), meta.get("page_token")
        if not (page_id.isdecimal() and token):
            print("::warning::" + account + " non connectée : aucun audit de cette Page.")
            continue
        if account == "meta_pronos" and page_id != RQ_ID:
            raise DeliveryError("ID de RQ Pronos inattendu : audit interrompu.")
        print("::notice::AUDIT SANS SUPPRESSION Page=" + account + " ID=" + page_id)
        entries = fetch_posts(graph, page_id, token)
        candidates, keep_2026, keep_other, uncertain = classify(entries, page_id)
        print("::notice::" + account +
              " : ANCIENNES_AVANT_2026=" + str(len(candidates)) +
              " ; CONSERVER_2026_ET_APRES=" + str(len(keep_2026)) +
              " ; AUTRES_CONSERVEES=" + str(len(keep_other)) +
              " ; INCERTAINES_CONSERVEES=" + str(len(uncertain)))
        for ident, stamp in candidates[:12]:
            print("::notice::A_EXAMINER_AVANT_2026 " + account + " " + stamp + " " + ident)
    print("::notice::FIN AUDIT : ZERO SUPPRESSION. Toutes les publications depuis 2026 conservées.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("::error::Audit en lecture seule échoué : " +
              (str(e) if isinstance(e, DeliveryError) else type(e).__name__))
        sys.exit(1)
