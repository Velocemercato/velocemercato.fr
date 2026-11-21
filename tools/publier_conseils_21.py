"""Diffuse une fois l’édition de conseils du 21 novembre sur les comptes VM reliés."""
import datetime as dt
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.diffuser_jt import DeliveryError, State, git_save
from tools.publier_meta import Graph, instagram_image
from tools.publier_tanzi_meta import page_matches, permalink

PAGE = "https://velocemercato.fr/conseils/#conseils-2026-11-21"
IMAGE = "https://velocemercato.fr/conseils/affiches/conseils-2026-11-21.jpg"
TEXT = (
    "⚽ Les conseils du soir de la VÉLOCE TEAM sont en ligne. "
    "Lives prévus ce soir pour les membres du groupe. Le VIP est gratuit à vie : "
    "retrouve les fiches et le lien d’inscription sur velocemercato.fr/conseils/.\n\n"
    "18+ · Jouer comporte des risques. Cotes relevées avant les rencontres."
)
KEY = "conseils-2026-11-21"

def wait_for_site():
    for _ in range(18):
        try:
            with urlopen(Request(IMAGE, method="HEAD"), timeout=10) as response:
                if response.headers.get_content_type() == "image/jpeg":
                    return
        except OSError:
            pass
        time.sleep(10)
    raise DeliveryError("Visuel public indisponible au moment de la diffusion.")

def publish(state, graph):
    wait_for_site()
    receipts = state.data.setdefault("conseils_publications", {})
    errors = 0
    for account in ("meta", "meta_pronos", "meta_univers"):
        page = (state.data.get("tokens") or {}).get(account) or {}
        if not page_matches(account, page):
            print(f"::warning::{account} compte non relié ou identité non vérifiée.", flush=True)
            errors += 1
            continue
        page_id = str(page["page_id"])
        token = page["page_token"]
        networks = ["facebook"]
        if page.get("ig_id"):
            networks.append("instagram")
        elif account != "meta_pronos":
            print(f"::warning::{account} aucun compte Instagram relié.", flush=True)
            errors += 1
        for network in networks:
            key = f"{KEY}/{account}/{network}"
            if key in receipts:
                print(f"{account} {network} : accusé déjà présent.", flush=True)
                continue
            receipts[key] = {"status": "envoi", "date": dt.datetime.now(dt.timezone.utc).isoformat()}
            state.save()
            try:
                if network == "facebook":
                    result = graph.call("POST", f"{page_id}/photos", {
                        "url": IMAGE, "caption": TEXT + "\n\n" + PAGE, "access_token": token
                    })
                    ident = str(result.get("post_id") or "")
                    link = permalink(graph, token, page_id, ident)
                else:
                    ident = str(instagram_image(graph, page, IMAGE, TEXT) or "")
                    if not ident.isdecimal():
                        raise DeliveryError("Identifiant Instagram absent.")
                    proof = graph.call("GET", ident, {"fields": "id,permalink", "access_token": token})
                    link = str(proof.get("permalink") or "")
                    if str(proof.get("id")) != ident or not link.startswith("https://www.instagram.com/"):
                        raise DeliveryError("Lien Instagram non confirmé.")
                receipts[key] = {"status": "publie_confirme", "url": link}
                state.save()
                print(f"::notice::CONFIRMÉ {account} {network} {link}", flush=True)
            except (DeliveryError, OSError, ValueError) as error:
                print(f"::error::{account} {network} {type(error).__name__}"
                      + (f" {str(error)[:150]}" if isinstance(error, DeliveryError) else ""), flush=True)
                errors += 1
    return not errors

if __name__ == "__main__":
    path = Path(os.environ["RUNNER_TEMP"]) / "vm-broadcast-state" / "state.enc"
    sys.exit(0 if publish(State(path, os.environ["VM_DIFFUSION_STATE_KEY"], lambda: git_save(path)), Graph()) else 1)
