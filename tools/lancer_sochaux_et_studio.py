"""Diffuser le guide Sochaux et un focus VM Studio, chacun sur sa page éditoriale."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, git_save, DeliveryError
from tools.editorial_vm import confirm, current_posts, identity, ledger, normal
from tools.publier_meta import Graph, ensure_meta_targets

PARIS = ZoneInfo("Europe/Paris")
SOCHAUX = "https://velocemercato.fr/en/fc-sochaux-guide/?utm_source=facebook&utm_medium=organic_social&utm_campaign=vm_anglais_novembre&utm_content=vm_actus_sochaux"
STUDIO = "https://vmunivers.fr/professionnels/?utm_source=facebook&utm_medium=organic_social&utm_campaign=vm_projets_novembre&utm_content=focus_studio"
PUBLICATIONS = (
    ("meta_pronos", "sochaux-premier-guide", "Quand Sochaux a changé le foot français", SOCHAUX,
     "Avant le premier championnat professionnel, le club de Sochaux avait déjà lancé la Coupe Peugeot. "
     "On raconte cette histoire dans notre nouveau guide en anglais, pour faire découvrir les clubs français aux supporters d’ailleurs.\n\n"
     "Quel autre club de l’Est mérite un portrait ? Retrouvez la série sur Véloce Mercato.\n"
     "https://www.facebook.com/velocemercato.fr/"),
    ("meta_univers", "studio-projets-concrets", "VM Studio · Votre activité en ligne", STUDIO,
     "Un client cherche vos horaires ou veut voir ce que vous faites. Une page claire peut lui donner les deux, "
     "avec vos photos et un moyen de vous contacter.\n\n"
     "Sur VM Univers, découvrez les exemples de sites et les offres pour les commerces, artisans et associations. "
     "Commencez par le modèle qui ressemble le plus à votre activité."),
)


def poster(state, graph, compte, ref, titre, lien, texte):
    cible = state.data.get("tokens", {}).get(compte) or {}
    compte_verifie = identity(graph, cible, compte, "facebook")
    done = ledger(state, compte)
    id_recu = "editorial/facebook/" + ("projet" if compte == "meta_univers" else "foot") + "/" + ref
    if id_recu in done:
        recu = done[id_recu]
        if recu.get("status") == "a_verifier" and recu.get("id"):
            try:
                url = confirm(graph, cible, "facebook", recu["id"])
            except DeliveryError:
                return recu
            recu.update(status="publie_confirme", url=url)
            state.save()
        return recu
    if any(normal(titre) in item for item in current_posts(graph, cible, "facebook")):
        return {"status": "deja_present"}
    recu = {"status": "envoi", "at": dt.datetime.now(PARIS).isoformat(), "title": titre, "identity": compte_verifie}
    done[id_recu] = recu
    state.save()
    try:
        r = graph.call("POST", cible["page_id"] + "/feed",
                       {"message": titre + "\n\n" + texte + "\n\n" + lien,
                        "link": lien, "access_token": cible["page_token"]})
        recu.update(status="a_verifier", id=str(r.get("id") or ""))
        state.save()
        recu.update(status="publie_confirme", url=confirm(graph, cible, "facebook", recu["id"]))
    except DeliveryError:
        recu.update(status="a_verifier")
    state.save()
    return recu


def main():
    if dt.datetime.now(PARIS).date().isoformat() != "2026-11-22":
        return 0
    chemin = Path(sys.argv[1])
    state = State(chemin, os.environ.get("VM_DIFFUSION_STATE_KEY", ""), lambda: git_save(chemin))
    ensure_meta_targets(state)
    graph = Graph()
    reussites = []
    for compte, *publication in PUBLICATIONS:
        try:
            recu = poster(state, graph, compte, *publication)
        except DeliveryError:
            recu = {"status": "identite_ou_historique_non_verifie"}
        print("VM_CROISSANCE " + json.dumps({"compte": compte, **recu}, ensure_ascii=False), flush=True)
        reussites.append(recu["status"] in ("publie_confirme", "deja_present"))
    return 0 if all(reussites) else 1


if __name__ == "__main__":
    sys.exit(main())
