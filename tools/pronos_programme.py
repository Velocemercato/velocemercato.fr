#!/usr/bin/env python3
"""Programme quotidien RQ Pronos : destination Facebook seule, vérification obligatoire.

AUCUNE publication sans :
  - VM_AUTO_PRONOS=true
  - le post unique "test/unique" confirmé dans l'état chiffré
  - identifiant de Page exact (VM_FACEBOOK_PRONOS_PAGE_ID)
Un seul post par créneau et jamais de doublon après erreur ou interruption.
Les 2 autres Pages et Instagram ne sont ni consultés ni modifiés.
"""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save
from tools.publier_meta import Graph
from tools.pronos_facebook import page_access, verify, normal, recent, prono, RISK

PARIS = ZoneInfo("Europe/Paris")
UTC = dt.timezone.utc
# Grille éditoriale en heure Europe/Paris. Le programme sélectionne les
# contenus existants et vérifiés; il ne fabrique ni JT, ni vidéo d'une heure.
# Les créneaux absents de contenu fiable restent vides, sans doublons.
# 04/11 (« go 1 + B » du propriétaire) : VM actus et pronos (≈1 490 abonnés) est la seule Page
# avec une audience réelle. Plus de foot et de JT, et une promotion quotidienne (16 h).
SLOTS = {7: "actus", 8: "foot", 9: "foot", 10: "belfort",
         11: "jt_foot", 12: "jt_actus", 13: "gaming", 14: "foot",
         15: "belfort", 16: "promo", 17: "foot", 18: "foot", 19: "actus", 20: "gaming",
         21: "jt"}
NEWS = {
    "foot": ("articles.json", "⚽", "https://velocemercato.fr/"),
    "actus": ("actus/news.json", "📰", "https://velocemercato.fr/pronos/"),
    "gaming": ("vm-gaming/news.json", "🎮", "https://velocemercato.fr/pronos/"),
}
PROJETS = (
    ("VM Univers", "https://vmunivers.fr/", "Découvre tous nos projets, sites et outils"),
    ("VM Gaming", "https://velocemercato.fr/vm-gaming/", "L'actualité des jeux vidéo et de la communauté"),
    ("VM Belfort", "https://velocemercato.fr/belfort/", "Les nouvelles et bons plans près de chez nous"),
    ("Véloce Mercato", "https://velocemercato.fr/", "L'actualité foot, sans les romans"),
)


def load_json(path, default):
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def safe_url(url):
    parsed = urlparse(str(url or ""))
    return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password


def article_candidates(universe, now):
    file, icon, site = NEWS[universe]
    rows = load_json(file, [])
    if not isinstance(rows, list):
        return []
    out = []
    for a in sorted(rows, key=lambda a: str(a.get("publishedAt", "")) if isinstance(a, dict) else "", reverse=True):
        if not isinstance(a, dict) or not recent(a.get("publishedAt"), now, 30):
            continue
        ident = str(a.get("id") or "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,99}", ident):
            continue
        sources = [s for s in a.get("sources", []) if isinstance(s, dict) and s.get("nom") and safe_url(s.get("url"))]
        if not sources or not a.get("titre") or not a.get("resume"):
            continue
        src = sources[0]
        link = site
        if universe == "foot" and (ROOT / "a" / (ident + ".html")).is_file():
            link = "https://velocemercato.fr/a/" + ident + ".html"
        # Ton autonome : résumé complet mais bref, différente accroche des comptes principaux.
        headline = normal(a["titre"])[:180]
        summary = normal(a["resume"])[:330]
        content = (f"{icon} LE POINT VM — {headline}\n\n{summary}\n\n"
                   f"Info d'après {normal(src['nom'])[:75]}. "
                   f"Lire la suite et les autres actus : {link}\n\n"
                   f"#RQPronos #{'Football' if universe == 'foot' else 'VMActus' if universe == 'actus' else 'VMGaming'}")
        out.append({"key": f"{universe}/{ident}", "text": content, "link": link})
    return out


def belfort_candidates(now):
    payload = load_json("belfort/actus.json", {})
    rows = payload.get("titres", []) if isinstance(payload, dict) else []
    out = []
    for a in rows:
        if not isinstance(a, dict) or not recent(a.get("d"), now, 28):
            continue
        if not (a.get("t") and a.get("s") and safe_url(a.get("u"))):
            continue
        import hashlib
        key = hashlib.sha256(a["u"].encode("utf-8")).hexdigest()[:20]
        title = normal(a["t"])[:200]
        link = a["u"]
        out.append({"key": "belfort/" + key,
                    "text": (f"📍 VM BELFORT · LE FLASH DU COIN\n\n{title}\n\n"
                             f"Information signalée par {normal(a['s'])[:80]}. "
                             f"Retrouve les détails directement chez le média source : {link}\n\n"
                             f"Les autres informations locales : https://velocemercato.fr/belfort/\n"
                             f"#Belfort #FrancheComte #VMUnivers"),
                    "link": link})
    return out


def jt_candidates(now, universe=None):
    rows = load_json("studio/diffusions.json", [])
    out = []
    for a in rows if isinstance(rows, list) else []:
        if not isinstance(a, dict) or not recent(a.get("date_publication"), now, 30):
            continue
        youtube = (a.get("plateformes") or {}).get("youtube") or {}
        url = str(youtube.get("url", ""))
        if youtube.get("status") != "published" or not re.fullmatch(r"https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}", url):
            continue
        ident = str(a.get("id", ""))
        if universe and not ident.startswith(universe + "-"):
            continue
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,99}", ident):
            continue
        out.append({"key": "jt/" + ident, "link": url,
                    "text": (f"🎬 LE JT DE L'UNIVERS VM\n\n{normal(a.get('titre'))[:200]}\n\n"
                             f"Les infos importantes en vidéo. Notre émission résume l'essentiel "
                             f"du jour : regarde-la ici 👉 {url}\n\n"
                             f"Émission réalisée avec l'aide de l'IA, informations sourcées.\n"
                             f"#JT #VeloceMercato #VMActus")})
    return out


# Pack éditorial ChatGPT (issue #161) : 10 textes SANS prix ni pari, calendrier de 4 semaines.
PROMO_TEXTES = {
    "studio_vitrine": ("https://vmunivers.fr/professionnels/",
        "Votre activité mérite un site clair, rapide et lisible sur téléphone. Découvrez les créations VM Studio "
        "et décrivez votre projet sans engagement : https://vmunivers.fr/professionnels/"),
    "studio_artisans": ("https://vmunivers.fr/professionnels/",
        "Artisans : présentez vos réalisations, horaires et coordonnées sur un site à votre image. "
        "Échangeons sur votre projet via https://vmunivers.fr/professionnels/"),
    "studio_commerces": ("https://vmunivers.fr/professionnels/",
        "Un commerce, une histoire, une vitrine numérique. VM Studio accompagne la présentation de votre activité : "
        "https://vmunivers.fr/professionnels/"),
    "studio_portfolio": ("https://vmunivers.fr/professionnels/",
        "Découvrez nos réalisations et les formules VM Studio. Chaque prestation fait l'objet d'un périmètre et "
        "d'un devis avant accord : https://vmunivers.fr/professionnels/"),
    "univers": ("https://vmunivers.fr/",
        "Un seul endroit pour explorer nos projets, médias et services : l'annuaire VM Univers. https://vmunivers.fr/"),
    "actu": ("https://velocemercato.fr/",
        "Le football et le mercato restent au cœur de Véloce Mercato. Retrouvez les articles complets sur https://velocemercato.fr/"),
    "jt": ("https://velocemercato.fr/",
        "Nos JT et formats courts vous donnent les grandes lignes ; les contenus complets sont à retrouver sur https://velocemercato.fr/"),
    "multisport": ("https://velocemercato.fr/multisport/",
        "Du football aux autres disciplines : découvrez les actualités et dossiers de Véloce Mercato. https://velocemercato.fr/multisport/"),
    "gaming_mangas": ("https://velocemercato.fr/",
        "Gaming, mangas, BD et séries : explorez les univers VM et leurs nouveautés depuis notre média. https://velocemercato.fr/"),
    "partenaires": ("https://vmunivers.fr/professionnels/",
        "Vous représentez un commerce, une association ou une entreprise ? Échangeons sur une collaboration éditoriale "
        "ou un espace partenaire, avec conditions et tarif annoncés à l'avance. https://vmunivers.fr/professionnels/"),
}
# Semaines S1 à S4, du lundi au dimanche (calendrier ChatGPT). Semaine 1 = celle du lundi 2 novembre 2026.
PROMO_CALENDRIER = (
    ("univers", "studio_vitrine", "actu", "jt", "studio_artisans", "gaming_mangas", "partenaires"),
    ("studio_portfolio", "multisport", "univers", "jt", "studio_commerces", "actu", "partenaires"),
    ("studio_artisans", "gaming_mangas", "studio_vitrine", "jt", "partenaires", "multisport", "univers"),
    ("studio_portfolio", "actu", "univers", "jt", "studio_commerces", "gaming_mangas", "partenaires"),
)
PROMO_DEBUT = dt.date(2026, 11, 2)


def promo_candidate(now):
    """Une promotion par jour au maximum, selon le calendrier : sans prix, sans pari, sans VIP."""
    local = now.astimezone(PARIS).date()
    jours = (local - PROMO_DEBUT).days
    semaine = (jours // 7) % len(PROMO_CALENDRIER)
    theme = PROMO_CALENDRIER[semaine][local.weekday()]
    link, text = PROMO_TEXTES[theme]
    return {"key": f"promo/{local:%Y-%m-%d}/{theme}", "link": link, "text": text + "\n\n#VeloceUniverse"}


def project_candidate(now):
    local = now.astimezone(PARIS)
    name, link, description = PROJETS[local.toordinal() % len(PROJETS)]
    return {"key": f"projet/{local:%Y-%m-%d}", "link": link,
            "text": (f"👑 LE PROJET VM DU JOUR : {name}\n\n{description}. "
                     f"Notre groupe développe aussi des médias foot, des JT et des outils gratuits.\n\n"
                     f"Découvrir 👉 {link}\n\n#VMUnivers #RQPronos")}


def preview_sourcee(now):
    """Agenda officiel du jour, chaque jour si le fichier vérifié existe."""
    local = now.astimezone(PARIS)
    today = local.date()
    # Aucun agenda ne doit être recopié du jour précédent.
    target = today
    filename = "programmes/avant_match_" + target.isoformat() + ".json"
    dataset = load_json(filename, {})
    if not isinstance(dataset, dict) or dataset.get("date_matchs") != target.isoformat():
        return None
    matches = dataset.get("matches") or []
    if len(matches) < 2:
        return None
    titre_jour = f"PROGRAMME DU {target:%d/%m/%Y}"
    lines = [
        "⚽ RQ PRONOS — AGENDA DU JOUR ET ANALYSE 100 % FICTIVE",
        "",
        titre_jour + " : LES MATCHS À SUIVRE 📊",
    ]
    for row in matches[:5]:
        sources = row.get("sources") or []
        # Un horaire sans preuve officielle bloque l'ensemble du programme.
        official_hosts = {"ligue1.com", "www.ligue1.com", "lfp.fr", "www.lfp.fr",
                          "liverpoolfc.com", "www.liverpoolfc.com", "lfcbeta.liverpoolfc.com",
                          "premierleague.com", "www.premierleague.com", "fplchallenge.premierleague.com"}
        if not (row.get("official_verified") is True and row.get("affiche")
                and row.get("heure_paris") and row.get("facts") and sources
                and all(safe_url(s.get("url")) and urlparse(s["url"]).hostname in official_hosts
                        for s in sources)):
            return None
        lines.extend(["", f"🏟️ {normal(row['affiche'])} — {normal(row['heure_paris'])} (Paris)"])
        for f in row["facts"][:2]:
            lines.append("• " + normal(f))
        lines.append("📎 Source : " + sources[0]["url"])
    lines.extend([
        "",
        "🧠 Analyse VM : calendrier et composition des équipes à vérifier avant les matchs. "
        "Aucun pourcentage 1/N/2 inventé.",
        "🎲 Simulation : bankroll théorique 100 points, aucune mise réelle. "
        "Un combiné multiplie les risques : aucun gain certain ni montante.",
        "",
        RISK,
        "#RQPronos #Football #VMUnivers",
    ])
    return {
        "key": "agenda/" + target.isoformat(),
        "text": "\n".join(lines),
        "link": "https://velocemercato.fr/pronos/",
    }


MENTION_PRONOS = "18+ · Aucun résultat garanti · Joueurs Info Service : 09 74 75 13 13"
ANNONCES_PRONOS = (
    "Le rendez-vous quotidien de la rubrique pronostics est à consulter sur notre site, et non dans nos publications "
    "Facebook : https://velocemercato.fr/pronos/. " + MENTION_PRONOS,
    "Notre page partage les actualités sportives ; la rubrique pronostics est accessible uniquement depuis "
    "https://velocemercato.fr/pronos/. " + MENTION_PRONOS,
    "Vous cherchez la rubrique pronostics VM ? Retrouvez les informations du jour directement sur "
    "https://velocemercato.fr/pronos/, sans sélection ni cote publiée ici. " + MENTION_PRONOS,
)


def annonce_pronos_du_jour(now):
    """Annonce « les pronos du jour sont en ligne » : uniquement un lien vers /pronos/,
    sans cote ni combiné dans le post, et seulement si une sélection du jour est active."""
    from tools.pronos_public import selection_active
    owner = load_json("pronos/selection.json", {})
    ia = load_json("pronos/analyse-claude.json", {})
    if not (selection_active(owner, now, True) or selection_active(ia, now, False)):
        return None
    # Annonce Facebook désactivée par défaut (demande du propriétaire, 04/11 :
    # pronos uniquement sur velocemercato.fr et VM Actus & Pronos).
    if not (owner.get("annonce_rq_pronos") is True or ia.get("annonce_rq_pronos") is True):
        return None
    local = now.astimezone(PARIS)
    anchor = "pronos-du-jour" if selection_active(owner, now, True) else "analyse-claude"
    return {"key": "pronos-du-jour/" + local.date().isoformat(),
            "link": "https://velocemercato.fr/pronos/",
            "text": ANNONCES_PRONOS[local.toordinal() % len(ANNONCES_PRONOS)]}


def candidates(now, kind):
    if kind in NEWS:
        return article_candidates(kind, now)
    if kind == "belfort":
        return belfort_candidates(now)
    if kind == "jt":
        return jt_candidates(now)
    if kind in ("jt_foot", "jt_actus", "jt_gaming"):
        return jt_candidates(now, kind.split("_", 1)[1])
    if kind == "week_summary":
        # Pas de faux "direct" ni de vidéo d'une heure si ce montage n'existe pas :
        # partager une émission hebdomadaire déjà réellement mise en ligne.
        # Chaque soir : une édition du jour réellement publiée, même sans magazine
        # hebdomadaire. Ne jamais annoncer 60 minutes sans vidéo confirmée.
        return jt_candidates(now)
    if kind == "projet":
        return [project_candidate(now)]
    if kind == "promo":
        return [promo_candidate(now)]
    if kind == "prono":
        # Un fichier prono.json peut dater de la veille alors que le match est fini.
        # Ne PAS republier un ancien pronostic sur le seul critère « créé <30h ».
        # Donner la priorité à l'agenda factuel dont les rencontres sont futures.
        annonce = annonce_pronos_du_jour(now)
        if annonce:
            return [annonce]
        verified_preview = preview_sourcee(now)
        if verified_preview:
            return [verified_preview]
        data = load_json("prono.json", {})
        match_date = str(data.get("match_date") or "") if isinstance(data, dict) else ""
        # Seul un prono portant une date de match explicite valide peut être relayé.
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", match_date):
            return []
        if match_date not in (now.astimezone(PARIS).date().isoformat(),
                              (now.astimezone(PARIS).date() + dt.timedelta(days=1)).isoformat()):
            return []
        selected = prono(now)
        return [selected] if selected else []
    return []


def publish_slot(state, graph, now=None):
    now = now or dt.datetime.now(UTC)
    if os.getenv("VM_AUTO_PRONOS") != "true":
        print("::notice::RQ Pronos désactivé : variable VM_AUTO_PRONOS différente de true.")
        return False
    account = page_access(state)
    page_id = str(account["page_id"])
    receipts = state.data.setdefault("meta_pronos_accuses", {})
    test = receipts.get("test/unique") or {}
    if test.get("status") != "publie_confirme":
        print("::notice::RQ Pronos protégé : le post test n'est pas encore confirmé. Aucun envoi.")
        return False
    if not str(test.get("id", "")).startswith(page_id + "_") or not str(test.get("url", "")).startswith("https://"):
        raise DeliveryError("Confirmation du test incohérente avec l'ID Facebook demandé.")
    local = now.astimezone(PARIS)
    # GitHub Actions peut déclencher le cron :25 plusieurs minutes en retard.
    # Identifier le CRON ORIGINAL, non l'heure réelle du runner : cela évite
    # d'ignorer une publication valide arrivée à :40, sans créer de doublon.
    regular_cron = os.getenv("VM_TRIGGER_CRON", "") == "25 5-21 * * *"
    special_cron = os.getenv("VM_TRIGGER_CRON", "") == "40 8-21 * * *"
    if local.hour == 10 and local.minute >= 35 and (special_cron or not regular_cron):
        kind = "prono"
        slot = f"creneau/{local:%Y-%m-%d}/10-prono"
    elif local.hour == 22 and local.minute >= 30 and (special_cron or not regular_cron):
        kind = "week_summary"
        slot = f"creneau/{local:%Y-%m-%d}/22h30-bilan"
    elif (local.minute >= 35 and not regular_cron) or special_cron:
        print("::notice::Ce déclenchement n'est pas un créneau éditorial à rattraper.")
        return False
    else:
        # Rattraper uniquement l'heure courante (pas de publication ancienne
        # ou d'un autre thème à la mauvaise heure).
        kind = SLOTS.get(local.hour)
        slot = f"creneau/{local:%Y-%m-%d}/{local.hour:02d}"
        if not kind:
            print("::notice::Aucun créneau éditorial à cette heure.")
            return False
    if slot in receipts:
        print("::notice::Créneau déjà traité : aucun doublon.")
        return False
    choice = next((p for p in candidates(now, kind)
                   if isinstance(p, dict) and p.get("key") and p["key"] != test.get("key")
                   and "post/" + p["key"] not in receipts and safe_url(p.get("link"))), None)
    if not choice:
        print("::notice::Aucune information récente et sourcée pour " + kind + ". Rien n'est publié.")
        return False
    key = "post/" + choice["key"]
    def save(receipt_key, status, **extra):
        receipts[receipt_key] = {"status": status, "at": now.isoformat(timespec="seconds"), **extra}
        state.save()
    # Acquittement AVANT l'appel API pour éviter toute rediffusion après une coupure.
    save(slot, "envoi", sujet=choice["key"])
    save(key, "envoi", creneau=slot)
    response = graph.call("POST", page_id + "/feed", {
        "message": choice["text"], "link": choice["link"], "access_token": account["page_token"]})
    post_id = str(response.get("id") or "")
    save(key, "envoye_a_verifier", id=post_id, creneau=slot)
    url = verify(graph, account["page_token"], page_id, post_id)
    save(key, "publie_confirme", id=post_id, url=url, creneau=slot)
    save(slot, "publie_confirme", sujet=choice["key"], id=post_id, url=url)
    print("::notice::RQ PRONOS : POST CONFIRMÉ, ID=" + post_id + " URL=" + url)
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    args = parser.parse_args()
    state = State(args.state, os.getenv("VM_DIFFUSION_STATE_KEY", ""),
                  lambda: git_save(args.state))
    publish_slot(state, Graph())


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("::error::" + (str(error) if isinstance(error, DeliveryError)
                             else "Échec publication RQ Pronos (" + type(error).__name__ + ")"))
        sys.exit(1)
