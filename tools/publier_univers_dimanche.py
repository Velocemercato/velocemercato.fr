#!/usr/bin/env python3
"""Campagne unique VM Univers, dimanche 1er novembre 2026.

Facebook Page 1349998758205153 + SON Instagram seulement.
Chaque envoi journalisé chiffré AVANT Meta pour exclure les doublons.
Jamais RQ Pronos ni VeloceMercato, aucun jeton imprimé.
"""
import datetime as dt
import os
import sys
import re
from pathlib import Path
from urllib import request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save
from tools.publier_meta import Graph, ensure_meta_targets, instagram_image

PAGE = "1349998758205153"
URL = "https://vmunivers.fr/studio/reseaux.html"
IMAGE = "https://vmunivers.fr/media/promos/vm-studio-paysage.jpg"
DAY = dt.date(2026, 11, 1)
PARIS = ZoneInfo("Europe/Paris")
PREFIX = "dimanche_vm_univers_2026-11-01"

FB_TEXT = (
    "👑 VM UNIVERS — LE PROGRAMME DU DIMANCHE EST LANCÉ !\n\n"
    "⚽ Le foot et les grands reportages, 📰 VM Actus, 🎮 VM Gaming, "
    "📍 les infos de VM Belfort… et les projets que nous construisons avec VM Studio.\n\n"
    "🎬 Tu as raté un JT ? Notre Kit Réseaux rassemble automatiquement "
    "les vidéos verticales, les actualités et les textes à partager.\n\n"
    "📲 Découvre le Kit Réseaux : " + URL + "\n"
    "🌐 Tous nos projets : https://vmunivers.fr/\n\n"
    "Le réseau VM, des idées et des projets. Dis-nous ce que tu aimerais voir ensuite !\n"
    "#VMUnivers #VMStudio #VMActus #VMGaming"
)

IG_TEXT = (
    "👑 VM UNIVERS — DES IDÉES, DES PROJETS, UN UNIVERS !\n\n"
    "Cette semaine encore, découvre nos médias, nos JT, le foot, le gaming, "
    "la vie locale et la création de sites avec VM Studio.\n\n"
    "📲 Notre nouveau Kit Réseaux se met à jour automatiquement : "
    "vidéos, actus et idées de posts prêts à partager.\n\n"
    "👉 vmunivers.fr/studio/reseaux.html — lien sur notre site.\n\n"
    "Quel projet VM t'intéresse le plus ? 💛\n"
    "#VMUnivers #VMStudio #Projets #Actualites #Gaming #VeloceMercato"
)


def valid_facebook(graph, token, post_id):
    if not re.fullmatch(PAGE + r"_[0-9]+", str(post_id)):
        raise DeliveryError("ID Facebook non conforme à VM Univers.")
    proof = graph.call("GET", post_id, {
        "fields": "id,from{id},permalink_url", "access_token": token})
    link = str(proof.get("permalink_url") or "")
    if (str(proof.get("id")) != post_id or
            str((proof.get("from") or {}).get("id")) != PAGE or
            not link.startswith(("https://www.facebook.com/", "https://m.facebook.com/"))):
        raise DeliveryError("Facebook : absence de confirmation de la Page et du lien.")
    return link


def available_image():
    try:
        req = request.Request(IMAGE, method="HEAD",
                              headers={"User-Agent": "VMUnivers-campaign/1.0"})
        with request.urlopen(req, timeout=25) as resp:
            ctype = str(resp.headers.get("Content-Type") or "").lower()
            return resp.status == 200 and ("image/jpeg" in ctype or "image/jpg" in ctype)
    except OSError:
        return False


def send(state, graph):
    now = dt.datetime.now(dt.timezone.utc)
    if now.astimezone(PARIS).date() != DAY:
        raise DeliveryError("Campagne autorisée le 1er novembre uniquement.")
    ensure_meta_targets(state)
    stored = state.data.get("tokens") or {}
    univers = stored.get("meta_univers") or {}
    if str(univers.get("page_id") or "") != PAGE or not univers.get("page_token"):
        raise DeliveryError("VM Univers : Page officielle non connectée.")
    if str(univers.get("ig_id") or "") and str(univers.get("ig_id")) == str((stored.get("meta") or {}).get("ig_id") or ""):
        raise DeliveryError("Instagram identique à celui de Véloce : refus.")
    token = univers["page_token"]
    record = state.data.setdefault("campagnes_univers", {})

    fb_key = PREFIX + "/facebook"
    if fb_key not in record:
        record[fb_key] = {"status": "envoi", "at": now.isoformat(), "page_id": PAGE}
        state.save()
        response = graph.call("POST", PAGE + "/feed",
                              {"message": FB_TEXT, "link": URL, "access_token": token})
        ident = str(response.get("id") or "")
        record[fb_key] = {"status": "envoye_a_verifier", "id": ident, "page_id": PAGE}
        state.save()
        link = valid_facebook(graph, token, ident)
        record[fb_key] = {"status": "publie_confirme", "id": ident, "url": link, "page_id": PAGE}
        state.save()
        print("::notice::VM UNIVERS FACEBOOK CONFIRMÉ " + ident + " URL=" + link, flush=True)
    else:
        print("::notice::VM UNIVERS FACEBOOK : déjà tenté, statut " + record[fb_key].get("status", "?"))

    if not univers.get("ig_id"):
        print("::notice::VM UNIVERS IG : non relié, aucun envoi.")
        return
    if not available_image():
        print("::warning::VM UNIVERS IG : image de marque non disponible, aucun envoi.")
        return
    ig_key = PREFIX + "/instagram"
    if ig_key in record:
        print("::notice::VM UNIVERS IG : déjà tenté, statut " + record[ig_key].get("status", "?"))
        return
    record[ig_key] = {"status": "envoi", "at": now.isoformat(),
                      "instagram_id": str(univers["ig_id"])}
    state.save()
    media_id = str(instagram_image(graph, univers, IMAGE, IG_TEXT) or "")
    record[ig_key] = {"status": "envoye_a_verifier", "id": media_id}
    state.save()
    if not media_id.isdecimal():
        raise DeliveryError("Instagram : publication non confirmée, aucun renvoi automatique.")
    proof = graph.call("GET", media_id, {
        "fields": "id,permalink,media_type", "access_token": token})
    link = str(proof.get("permalink") or "")
    if str(proof.get("id") or "") != media_id or not link.startswith("https://www.instagram.com/"):
        raise DeliveryError("Instagram : lien de publication non confirmé.")
    record[ig_key] = {"status": "publie_confirme", "id": media_id, "url": link}
    state.save()
    print("::notice::VM UNIVERS INSTAGRAM CONFIRMÉ " + media_id + " URL=" + link, flush=True)


if __name__ == "__main__":
    try:
        p = Path(os.environ["RUNNER_TEMP"]) / "vm-broadcast-state" / "state.enc"
        st = State(p, os.getenv("VM_DIFFUSION_STATE_KEY", ""),
                   lambda: git_save(p))
        send(st, Graph())
    except Exception as e:
        print("::error::VM UNIVERS : " + (
            str(e) if isinstance(e, DeliveryError) else type(e).__name__))
        sys.exit(1)
