#!/usr/bin/env python3
"""Publication exceptionnelle du portrait Loic Tanzi sur Pages deja reliees.

Un seul envoi maximum par reseau et par Page; accusé AVANT HTTP dans l'etat
chiffre. Aucun jeton, secret, ni identifiant de connexion n'est affiche.
"""
import datetime as dt
import os
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save
from tools.publier_meta import Graph, instagram_reel

PORTRAIT="https://velocemercato.fr/reportages/loic-tanzi.html"
VIDEO="https://velocemercato.fr/media/reportages/Reportage_Loic_Tanzi_mobile.mp4"
RQ_ID="112294796981981"
KEY="tanzi-2026-10-31"
TEXTS={
 "meta": (
    "🎬⚽ LOÏC TANZI : DU TERRAIN AUX PLATEAUX TÉLÉ !\n\n"
    "Chez Véloce Mercato, on adore regarder L'Équipe TV et toute son équipe. "
    "Et Loïc, avec ses analyses et sa spontanéité, nous fait franchement marrer 😄\n\n"
    "On a consacré un portrait vidéo à son parcours dans l'actualité football et le mercato. "
    "Le foot, l'essentiel et le sourire !\n\n"
    "🎥 Découvrir le reportage : "+PORTRAIT+"\n\n"
    "Portrait indépendant réalisé à partir de sources publiques, avec l'aide de l'IA : "
    "ce n'est ni une interview ni une collaboration avec Loïc Tanzi ou L'Équipe.\n\n"
    "#VeloceMercato #LoicTanzi #Lequipe #Football #Reportage"),
 "meta_pronos": (
    "⚽ RQ PRONOS · PORTRAIT FOOT\n\n"
    "🎬 LOÏC TANZI : DU TERRAIN AUX PLATEAUX TÉLÉ\n\n"
    "Tu regardes les débats mercato sur L'Équipe TV ? On apprécie la bande "
    "et Loïc nous fait souvent bien rire 😄\n\n"
    "Le portrait indépendant signé Véloce Mercato, en vidéo 👇\n"
    +PORTRAIT+"\n\n"
    "Réalisation illustrée avec l'aide de l'IA, d'après des sources publiques. "
    "Aucune interview ni collaboration officielle.\n\n"
    "#RQPronos #VeloceMercato #ActuFoot"),
 "meta_univers": (
    "👑 VM UNIVERS · GRAND REPORTAGE VÉLOCE MERCATO\n\n"
    "🎬 Découvre notre portrait de Loïc Tanzi et son parcours dans le journalisme football.\n\n"
    "On aime les débats et l'ambiance de L'Équipe TV, avec une mention spéciale à Loïc "
    "qui nous fait sourire 😄\n\n"
    "▶️ Regarder : "+PORTRAIT+"\n\n"
    "Portrait indépendant illustré avec l'aide de l'IA, sans interview ni collaboration "
    "avec la rédaction de L'Équipe.\n\n#VMUnivers #VeloceMercato #Reportage"),
}
IG_TEXT=(
 "🎬⚽ LOÏC TANZI · PORTRAIT VÉLOCE MERCATO\n\n"
 "On adore suivre L'Équipe TV et ses journalistes, et Loïc nous fait marrer 😄 "
 "Retour en images sur son parcours dans la presse football.\n\n"
 "Portrait indépendant : vidéo illustrée avec l'aide de l'IA à partir de sources publiques. "
 "Pas une interview ni une collaboration officielle.\n\n"
 "Retrouve l'article : velocemercato.fr/reportages/loic-tanzi.html (lien en bio).\n"
 "#LoicTanzi #VeloceMercato #Football #Reportage"
)

def page_matches(account, page):
    name=str(page.get("page_name") or "").lower().replace("é","e")
    page_id=str(page.get("page_id") or "")
    if not page_id.isdecimal() or not page.get("page_token"):
        return False
    if account=="meta_pronos":
        return page_id==RQ_ID and not page.get("ig_id")
    if account=="meta":
        return "veloce" in name and "univers" not in name and page_id!=RQ_ID
    if account=="meta_univers":
        return "univers" in name and page_id!=RQ_ID
    return False

def permalink(graph, token, page_id, post_id):
    if not re.fullmatch(r"[0-9]+_[0-9]+",str(post_id or "")) or not str(post_id).startswith(page_id+"_"):
        raise DeliveryError("ID de publication Facebook inattendu.")
    d=graph.call("GET",post_id,{"fields":"id,from{id},permalink_url","access_token":token})
    if str(d.get("id"))!=post_id or str((d.get("from") or {}).get("id"))!=page_id:
        raise DeliveryError("Impossible de verifier la Page d'origine du post Facebook.")
    url=str(d.get("permalink_url") or "")
    if not url.startswith(("https://www.facebook.com/","https://m.facebook.com/")):
        raise DeliveryError("Le lien de publication Facebook n'est pas confirme.")
    return url

def publish(state, graph):
    receipts=state.data.setdefault("tanzi_publications",{})
    errors=[]
    for account in ("meta","meta_pronos","meta_univers"):
        page=(state.data.get("tokens") or {}).get(account) or {}
        if not page_matches(account,page):
            print(f"::notice::Tanzi {account} : Page absente ou identite inattendue, aucun envoi.")
            continue
        page_id=str(page["page_id"])
        token=page["page_token"]
        k=KEY+"/"+account+"/fb"
        if k not in receipts:
            receipts[k]={"status":"envoi","page":page_id,"date":dt.datetime.now(dt.timezone.utc).isoformat()}
            state.save()
            try:
                result=graph.call("POST",page_id+"/feed",{
                    "message":TEXTS[account],"link":PORTRAIT,"access_token":token})
                post_id=str(result.get("id") or "")
                receipts[k]={"status":"envoye_a_verifier","page":page_id,"id":post_id}
                state.save()
                link=permalink(graph,token,page_id,post_id)
                receipts[k]={"status":"publie_confirme","page":page_id,"id":post_id,"url":link}
                state.save()
                print(f"::notice::TANZI FB {account} CONFIRME id={post_id} url={link}",flush=True)
            except (DeliveryError,OSError,ValueError) as e:
                errors.append(account+" Facebook: "+str(e)[:140])
        else:
            print(f"::notice::Tanzi {account} Facebook: {receipts[k].get('status')} (aucun doublon).")
        if account=="meta_pronos" or not page.get("ig_id"):
            continue
        if receipts[k].get("status")!="publie_confirme":
            continue
        ik=KEY+"/"+account+"/instagram"
        if ik in receipts:
            print(f"::notice::Tanzi {account} Instagram: {receipts[ik].get('status')} (aucun doublon).")
            continue
        receipts[ik]={"status":"envoi","date":dt.datetime.now(dt.timezone.utc).isoformat()}
        state.save()
        try:
            ig_id=str(instagram_reel(graph,page,{"verticale":VIDEO,"texte_vertical":IG_TEXT}) or "")
            receipts[ik]={"status":"envoye_a_verifier","id":ig_id}
            state.save()
            if not ig_id.isdecimal():
                raise DeliveryError("Instagram: aucun ID media confirme.")
            proof=graph.call("GET",ig_id,{"fields":"id,permalink","access_token":token})
            link=str(proof.get("permalink") or "")
            if str(proof.get("id"))!=ig_id or not link.startswith("https://www.instagram.com/"):
                raise DeliveryError("Instagram : lien media non confirme.")
            receipts[ik]={"status":"publie_confirme","id":ig_id,"url":link}
            state.save()
            print(f"::notice::TANZI INSTAGRAM {account} CONFIRME id={ig_id} url={link}",flush=True)
        except (DeliveryError,OSError,ValueError) as e:
            errors.append(account+" Instagram: "+str(e)[:140])
    for err in errors:
        print("::error::TANZI "+err)
    return not errors

if __name__=="__main__":
    try:
        folder=Path(os.environ["RUNNER_TEMP"])/"vm-broadcast-state"
        file=folder/"state.enc"
        state=State(file,os.getenv("VM_DIFFUSION_STATE_KEY",""),lambda:git_save(file))
        sys.exit(0 if publish(state,Graph()) else 1)
    except Exception as e:
        print("::error::TANZI "+(str(e) if isinstance(e,DeliveryError) else type(e).__name__))
        sys.exit(1)
