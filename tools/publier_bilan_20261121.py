"""Diffusion unique du bilan VM sur les trois pages et les deux comptes éditoriaux."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.bilan_vm_20261116 import send_instagram
from tools.diffuser_jt import State, git_save, DeliveryError
from tools.editorial_vm import identity, current_posts, instagram_room, confirm, normal, ledger
from tools.publier_meta import Graph, ensure_meta_targets

LINK = "https://velocemercato.fr/conseils/#resultats-2026-11-21"
IMAGE = "https://velocemercato.fr/conseils/preuves/2026-11-21-bilan-vm.jpg"
TITLE = "VM · Bilan du 21 novembre"
TARGETS = (
    ("meta", "facebook"), ("meta_univers", "facebook"), ("meta_pronos", "facebook"),
    ("meta", "instagram"), ("meta_univers", "instagram"),
)
PARIS = ZoneInfo("Europe/Paris")
DETAILS = """2 conseils réussis sur 4, d’après les tickets réglés.
✅ France −16 et Naples vainqueur · cote 2,06
✅ Knicks vainqueurs et Verstappen vainqueur · cote 2,75
❌ Monaco, Mbappé et Calgary +1 · cote 2,28
❌ Les deux équipes marquent · cote 2,35, bloqué par Dallas–Portland

Bilan théorique de la soirée à mise égale : +20,25 %.
"""
ANNONCE = """Vous voulez une édition gratuite en public ce soir ? Dites-le en commentaire avant 18 h (heure de Paris). Si vous êtes nombreux à la demander, on la partagera en public.
"""
CONTACT = """📌 Bilan complet et demande d’accès au VIP gratuit : velocemercato.fr/conseils/

18+ · Jouer comporte des risques. Joueurs Info Service : 09 74 75 13 13."""


def texte(now):
    if now.date().isoformat() == "2026-11-22" and now.hour < 18:
        return TITLE + "\n\n" + DETAILS + "\n" + ANNONCE + "\n" + CONTACT
    return TITLE + "\n\n" + DETAILS + "\n" + CONTACT


def envoyer_instagram(graph, meta, caption):
    import tools.bilan_vm_20261116 as reutilisation
    # La fonction commune prépare le conteneur, attend le statut FINISHED puis le publie.
    reutilisation.TEXT = caption
    return send_instagram(graph, meta, IMAGE)


def confirmer_instagram_en_attente(state, graph, account, receipt):
    meta = state.data.get("tokens", {}).get(account) or {}
    identity(graph, meta, account, "instagram")
    data = graph.call("GET", str(meta["ig_id"]) + "/media",
                      {"fields": "id,caption,timestamp", "limit": 25, "access_token": meta["page_token"]}).get("data")
    if not isinstance(data, list):
        raise DeliveryError("Historique Instagram non vérifiable.")
    messages = [p for p in data if normal(TITLE) in normal(p.get("caption") or "")
                and "20,25" in (p.get("caption") or "")]
    if len(messages) != 1 or not str(messages[0].get("id") or "").isdigit():
        return receipt
    ident = str(messages[0]["id"])
    url = confirm(graph, meta, "instagram", ident)
    receipt.update(status="publie_confirme", id=ident, url=url)
    state.save()
    return receipt


def publier(state, graph, account, network):
    key = "editorial/" + network + "/bilan/2026-11-21"
    done = ledger(state, account)
    if key in done:
        receipt = done[key]
        if network == "instagram" and receipt.get("status") in ("envoi", "envoye_a_verifier", "a_verifier_sans_renvoi"):
            return confirmer_instagram_en_attente(state, graph, account, receipt)
        return receipt
    meta = state.data.get("tokens", {}).get(account) or {}
    who = identity(graph, meta, account, network)
    if any(normal(TITLE) in item for item in current_posts(graph, meta, network)):
        return {"status": "deja_present"}
    if network == "facebook":
        scheduled = graph.call("GET", meta["page_id"] + "/scheduled_posts",
                               {"fields": "id,message", "limit": 100, "access_token": meta["page_token"]})
        if not isinstance(scheduled.get("data"), list):
            raise DeliveryError("Publications programmées non vérifiables.")
        if any(normal(TITLE) in normal(row.get("message")) for row in scheduled["data"]):
            return {"status": "deja_programme"}
    elif instagram_room(graph, meta) < 1:
        return {"status": "quota_atteint"}
    now = dt.datetime.now(PARIS)
    caption = texte(now)
    if network == "facebook":
        caption = caption.replace("velocemercato.fr/conseils/", LINK, 1)
    receipt = {"status": "envoi", "at": now.isoformat(), "title": TITLE, "identity": who}
    done[key] = receipt
    state.save()
    try:
        if network == "facebook":
            result = graph.call("POST", meta["page_id"] + "/photos",
                                {"caption": caption, "url": IMAGE, "access_token": meta["page_token"]})
            ident = str(result.get("post_id") or "")
        else:
            ident = envoyer_instagram(graph, meta, caption)
        receipt.update(status="envoye_a_verifier", id=ident)
        state.save()
        receipt.update(status="publie_confirme", url=confirm(graph, meta, network, ident))
    except DeliveryError:
        receipt.update(status="a_verifier_sans_renvoi")
    state.save()
    return receipt


def main():
    path = Path(sys.argv[1])
    state = State(path, os.environ.get("VM_DIFFUSION_STATE_KEY", ""), lambda: git_save(path))
    ensure_meta_targets(state)
    graph = Graph()
    confirmations = []
    for account, network in TARGETS:
        try:
            receipt = publier(state, graph, account, network)
        except (DeliveryError, KeyError) as exc:
            import re
            code = re.search(r"Meta a refusé \(([0-9]+), code ([0-9?]+)\)", str(exc))
            receipt = {"status": "bloque", "raison": "Meta " + "/".join(code.groups()) if code else type(exc).__name__}
        result = {**receipt, "destination": account + "/" + network}
        print("VM_BILAN_RECEIPT " + json.dumps(result, ensure_ascii=False), flush=True)
        confirmations.append(result.get("status") in ("publie_confirme", "deja_present", "deja_programme"))
    return 0 if all(confirmations) else 1


if __name__ == "__main__":
    sys.exit(main())
