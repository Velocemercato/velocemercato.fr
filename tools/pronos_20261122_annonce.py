"""Partager le lien de la carte du 22 novembre sur les trois pages Facebook VM."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, git_save, DeliveryError
from tools.editorial_vm import identity, current_posts, confirm, normal, ledger
from tools.publier_meta import Graph, ensure_meta_targets

PARIS = ZoneInfo("Europe/Paris")
TITRE = "VM · Les pronos multisports du 22 novembre"
LIEN = "https://velocemercato.fr/conseils/#conseils-2026-11-22"
MESSAGE = f"""{TITRE}

L’édition publique est en ligne. Les quatre fiches, les sélections et toutes les analyses sont sur Véloce Mercato.
{LIEN}

Réservé aux 18 ans et plus. Jouer comporte des risques. Joueurs Info Service : 09 74 75 13 13."""
CIBLES = ("meta", "meta_univers", "meta_pronos")
CLE = "editorial/facebook/conseils/2026-11-22"


def edition_ouverte(maintenant):
    return maintenant.date() == dt.date(2026, 11, 22) and maintenant.hour < 18


def publier(graph, state, cible):
    traces = ledger(state, cible)
    meta = state.data.get("tokens", {}).get(cible) or {}
    compte = identity(graph, meta, cible, "facebook")
    if CLE in traces:
        recu = traces[CLE]
        if recu.get("status") == "a_verifier" and recu.get("id"):
            try:
                url = confirm(graph, meta, "facebook", recu["id"])
            except DeliveryError:
                return recu
            recu.update(status="publie_confirme", url=url)
            state.save()
        return recu
    if any(normal(TITRE) in texte for texte in current_posts(graph, meta, "facebook")):
        return {"status": "deja_present"}
    moment = dt.datetime.now(PARIS)
    if not edition_ouverte(moment):
        return {"status": "edition_close"}
    recu = {"status": "envoi", "at": moment.isoformat(), "identity": compte}
    traces[CLE] = recu
    state.save()
    try:
        resultat = graph.call("POST", meta["page_id"] + "/feed", {
            "message": MESSAGE, "link": LIEN, "access_token": meta["page_token"],
        })
        recu.update(status="a_verifier", id=str(resultat.get("id") or ""))
        state.save()
        recu.update(status="publie_confirme", url=confirm(graph, meta, "facebook", recu["id"]))
    except DeliveryError:
        recu.update(status="a_verifier")
    state.save()
    return recu


def main():
    chemin = Path(sys.argv[1])
    state = State(chemin, os.environ.get("VM_DIFFUSION_STATE_KEY", ""), lambda: git_save(chemin))
    ensure_meta_targets(state)
    graph = Graph()
    bilan = []
    for cible in CIBLES:
        try:
            recu = publier(graph, state, cible)
        except DeliveryError:
            recu = {"status": "verification_impossible"}
        print("VM_CONSEILS_RECEIPT " + json.dumps({"destination": cible, **recu}, ensure_ascii=False), flush=True)
        bilan.append(recu["status"] in ("publie_confirme", "deja_present"))
    return 0 if all(bilan) else 1


if __name__ == "__main__":
    sys.exit(main())
