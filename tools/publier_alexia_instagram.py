#!/usr/bin/env python3
"""Un seul Reel Alexia Depagne sur Instagram Véloce Mercato. ZÉRO Facebook.

L'identité de la Page et de l'Instagram lié est contrôlée ; intention sauvegardée
chiffrée AVANT le premier appel de publication. Pas de répétition automatique.
"""
import datetime as dt
import os
import sys
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save
from tools.publier_meta import Graph, instagram_reel

VIDEO="https://velocemercato.fr/media/reportages/Reportage_Alexia_Depagne_instagram.mp4"
PORTRAIT="https://velocemercato.fr/reportages/alexia-depagne.html"
KEY="alexia-depagne/reel-studio-instagram-2026-10-31"
CAPTION=(
    "🎬 LE GRAND REPORTAGE VÉLOCE MERCATO\n\n"
    "🇫🇷 ALEXIA DEPAGNE — DU BABY-FOOT DE LOISIR À L'ÉQUIPE DE FRANCE !\n\n"
    "De ses débuts à la fête foraine à la compétition internationale, "
    "découvre le beau parcours d'une passionnée qui veut faire grandir "
    "la place des femmes autour des tables. ⚽🏆\n\n"
    "🎙️ Notre portrait en images, avec voix de synthèse, "
    "réalisé à partir de sources publiques et de photos transmises "
    "par les proches d'Alexia. Merci à eux ! "
    "Ce n'est pas une interview ni une collaboration officielle.\n\n"
    "📖 Le reportage complet : velocemercato.fr/reportages/alexia-depagne.html\n\n"
    "#AlexiaDepagne #BabyFoot #EquipeDeFrance #SportFeminin #VeloceMercato #GrandReportage"
)


def publish(state, graph):
    accounts=state.data.get("tokens") or {}
    meta=accounts.get("meta") or {}
    page_id=str(meta.get("page_id") or "")
    name=str(meta.get("page_name") or "").lower().replace("é","e").replace("è","e")
    ig_id=str(meta.get("ig_id") or "")
    if not (page_id.isdecimal() and ig_id.isdecimal() and meta.get("page_token")
            and "veloce" in name and "univers" not in name):
        raise DeliveryError("Instagram Véloce Mercato non relié ou identité incorrecte : refus.")
    if page_id in {str((accounts.get(k) or {}).get("page_id")) for k in ("meta_univers","meta_pronos")}:
        raise DeliveryError("Identifiant Facebook partagé : refus de choisir Instagram automatiquement.")
    if ig_id==str((accounts.get("meta_univers") or {}).get("ig_id") or ""):
        raise DeliveryError("Instagram VM Univers distinct non vérifié : refus.")
    rec=state.data.setdefault("alexia_instagram",{})
    if rec.get(KEY):
        print("::notice::ALEXIA INSTAGRAM : déjà tenté, statut="+str(rec[KEY].get("status")))
        return rec[KEY].get("status")=="publie_confirme"
    # Contrôle public avant de tenter l'envoi.
    import urllib.request
    try:
        request=urllib.request.Request(VIDEO,method="HEAD",headers={"User-Agent":"VM-Reel-Publisher/1.0"})
        with urllib.request.urlopen(request,timeout=30) as resp:
            mime=str(resp.headers.get("Content-Type") or "").lower()
            length=int(resp.headers.get("Content-Length") or 0)
            if resp.status!=200 or "video/" not in mime or length<100_000:
                raise DeliveryError("Le MP4 n'est pas encore disponible sur le site public.")
    except (OSError,ValueError) as exc:
        raise DeliveryError("Le MP4 public n'est pas encore lisible : aucun Reel envoyé.") from None

    rec[KEY]={"status":"envoi","at":dt.datetime.now(dt.timezone.utc).isoformat(),
              "instagram_id":ig_id,"video":VIDEO}
    state.save()
    reel_id=str(instagram_reel(graph,meta,{"verticale":VIDEO,"texte_vertical":CAPTION}) or "")
    rec[KEY]={"status":"envoye_a_verifier","id":reel_id,"instagram_id":ig_id}
    state.save()
    if not reel_id.isdecimal():
        raise DeliveryError("Instagram : création non confirmée, aucune nouvelle tentative.")
    proof=graph.call("GET",reel_id,{"fields":"id,permalink,media_type,username",
                                    "access_token":meta["page_token"]})
    link=str(proof.get("permalink") or "")
    if str(proof.get("id"))!=reel_id or not link.startswith("https://www.instagram.com/"):
        raise DeliveryError("Reel envoyé mais lien non vérifié, refus d'un doublon.")
    rec[KEY]={"status":"publie_confirme","id":reel_id,"url":link,
              "instagram_id":ig_id}
    state.save()
    print("::notice::REEL ALEXIA INSTAGRAM CONFIRMÉ : "+link,flush=True)
    return True


if __name__=="__main__":
    try:
        f=Path(os.environ["RUNNER_TEMP"])/"vm-broadcast-state"/"state.enc"
        state=State(f,os.getenv("VM_DIFFUSION_STATE_KEY",""),lambda:git_save(f))
        sys.exit(0 if publish(state,Graph()) else 1)
    except Exception as e:
        print("::error::ALEXIA INSTAGRAM : "+(
            str(e) if isinstance(e,DeliveryError) else type(e).__name__))
        sys.exit(1)
