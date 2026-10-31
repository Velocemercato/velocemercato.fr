#!/usr/bin/env python3
"""Audit EN LECTURE SEULE des publications historiques de RQ Pronos.

Ne supprime ni ne modifie AUCUNE publication Facebook.
La date protégée est explicitement 2026-10-31, fuseau Europe/Paris :
préserver toutes les publications à partir du 31 octobre 00:00, sans changer
cette limite si le robot est relancé un autre jour.
"""
import datetime as dt
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError
from tools.pronos_facebook import page_access
from tools.publier_meta import Graph

PARIS = ZoneInfo("Europe/Paris")
PROTECTED_START = dt.datetime(2026, 10, 31, 0, 0, tzinfo=PARIS)
MAX_PAGES = 20
MAX_POSTS = 1500


def fetch_posts(graph, page_id, token):
    rows, cursor, seen_cursors = [], None, set()
    for page in range(MAX_PAGES):
        args = {
            "fields": "id,created_time,permalink_url,from{id}",
            "limit": 100,
            "access_token": token,
        }
        if cursor:
            args["after"] = cursor
        answer = graph.call("GET", page_id + "/published_posts", args)
        batch = answer.get("data")
        if not isinstance(batch, list):
            raise DeliveryError("Meta : /published_posts ne retourne pas de liste.")
        rows.extend(batch)
        if len(rows) > MAX_POSTS:
            raise DeliveryError("Trop de publications pour garantir un audit complet.")
        paging = answer.get("paging") or {}
        nxt = paging.get("next")
        if not nxt:
            break
        new_cursor = (paging.get("cursors") or {}).get("after")
        if not new_cursor or new_cursor in seen_cursors:
            raise DeliveryError("Pagination Facebook incomplète : audit annulé.")
        seen_cursors.add(new_cursor)
        cursor = new_cursor
    else:
        raise DeliveryError("Pagination interrompue avant la fin : audit non valide.")
    return rows


def audit(state, graph):
    page = page_access(state)
    page_id = str(page["page_id"])
    print("::notice::AUDIT RQ PRONOS SANS SUPPRESSION ; page ID " + page_id)
    entries = fetch_posts(graph, page_id, page["page_token"])
    older, protected, uncertain = [], [], []
    seen_ids = set()
    for entry in entries:
        ident = str(entry.get("id") or "")
        if ident in seen_ids:
            continue
        seen_ids.add(ident)
        if not ident.startswith(page_id + "_"):
            uncertain.append(ident)
            continue
        creator = str((entry.get("from") or {}).get("id") or "")
        if creator and creator != page_id:
            uncertain.append(ident)
            continue
        raw_time = str(entry.get("created_time") or "")
        try:
            date = dt.datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            if date.tzinfo is None:
                raise ValueError("timezone missing")
            local = date.astimezone(PARIS)
        except (ValueError, TypeError):
            uncertain.append(ident)
            continue
        if local < PROTECTED_START:
            older.append((ident, local.isoformat()))
        else:
            protected.append((ident, local.isoformat()))
    print("::notice::PUBLICATIONS_LISTEES=" + str(len(seen_ids)))
    print("::notice::AVANT_31_OCTOBRE_A_EXAMINER=" + str(len(older)))
    print("::notice::DU_31_OCTOBRE_ET_APRES_A_CONSERVER=" + str(len(protected)))
    print("::notice::IDENTITE_OU_DATE_INCERTAINE_A_CONSERVER=" + str(len(uncertain)))
    for ident, stamp in protected[:20]:
        print("::notice::CONSERVER " + stamp + " / " + ident)
    for ident, stamp in older[:8]:
        print("::notice::ANCIEN_A_EXAMINER " + stamp + " / " + ident)
    print("::notice::AUCUNE SUPPRESSION NI MODIFICATION EFFECTUEE")
    return len(older), len(protected), len(uncertain)


if __name__ == "__main__":
    state_path = Path(os.environ["RUNNER_TEMP"]) / "vm-broadcast-state" / "state.enc"
    try:
        state = State(state_path, os.environ.get("VM_DIFFUSION_STATE_KEY", ""))
        audit(state, Graph())
    except Exception as e:
        print("::error::AUDIT RQ PRONOS : " + (
            str(e) if isinstance(e, DeliveryError) else type(e).__name__))
        sys.exit(1)
