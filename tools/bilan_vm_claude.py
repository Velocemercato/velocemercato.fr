"""Synthèse de passation construite à partir des reçus publics, pas d'un succès de workflow seul."""
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]


def read(path,default):
    try:return json.loads((ROOT/path).read_text())
    except (OSError,ValueError):return default


def main():
    status=read('studio/editorial-status.json',{})
    audit=read('docs/AUDIT_CLAUDE_2026-11-11.json',{})
    sources=read('sources/flux-valides.json',{})
    teasers=read('studio/teasers.json',{})
    confirmed={}
    for event in [status]+status.get('history',[]):
        for row in event.get('confirmed',[]):confirmed[row['target']+'/'+row['id']]=row
        for target,data in event.get('targets',{}).items():
            for row in data.get('posts',[]):confirmed[target+'/'+row['id']]={**row,'target':target}
    names={'meta':'Véloce Mercato','meta_pronos':'VM Actus et Pronos','meta_univers':'VM Univers'}
    lines=['# Dossier Claude — Véloce Mercato, site et réseaux','',
           'État établi le '+dt.datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='minutes')+'.', '',
           'Ce dossier remplace les anciennes consignes de restauration intégrale et les anciennes cadences. Il décrit le travail autorisé par Romain dans cette conversation. Les accès et conversations de ChatGPT ne sont pas automatiquement accessibles dans Claude.', '',
           '## Guide des accès pour Claude', '',
           'Lire [ACCES_CLAUDE_VM_2026-11-11.md](ACCES_CLAUDE_VM_2026-11-11.md) : dépôts, Cloudflare, connexions Meta, marque Metricool, programmateur TikTok, contrôles et accès à connecter dans Claude. Aucun secret n’est inclus et aucun accès Claude n’a été créé automatiquement.', '',
           '## Priorités et périmètre','',
           '- Conserver l’accueil bureau et tous les boutons validés. Le site vitrine vmunivers.fr conserve sa présentation : seul son tableau de réseaux a été modifié à la demande suivante de Romain.',
           '- Le volet Foot propose « Ouvrir la rubrique complète » vers https://velocemercato.fr/foot/. Cette page reprend index.html du commit d488e7e20ea3db047e026465139156f5dd109445, dernier changement de cette page avant 21 h Paris le 4 novembre 2026. Ses fichiers JSON sont les flux actuels, pas les informations figées du 4 novembre.',
           '- Vérifier la rubrique Foot et ses lecteurs sur téléphone avant toute autre refonte. Ne pas remplacer le bureau par l’ancien accueil.',
           '- Les conseils pronos restent gérés avec Romain ; le pouf VM Prono ouvre https://t.me/VMCONSEILSPRONOS. Ne pas inventer de conseil ou de résultat.', '',
           '## Carte des accès du bureau','',
           '| Élément | Destination |','|---|---|',
           '| Logo VM rond près du titre | https://vmunivers.fr/ |',
           '| Micro | Facebook Véloce Mercato |',
           '| Fauteuil, plaque Facebook VMunivers.fr | Facebook VM Univers |',
           '| Globe, plaque Facebook VM Actus Pronos | Facebook VM Actus et Pronos |',
           '| Pouf VM PRONO · TELEGRAM | https://t.me/VMCONSEILSPRONOS |',
           '| Cadres | Foot, Multisport sans Foot, Actus et régions, Gaming, Manga & Séries, Studio, Pastilles |',
           '| Réseaux en bas | Les deux Facebook et les Instagram/TikTok ajoutés par Romain ; YouTube, Snapchat, Discord, Twitch conservés |','',
           '## Correction complémentaire du tableau VM Univers','', 'Sur vmunivers.fr, Romain a demandé : première case à gauche Facebook https://www.facebook.com/share/1FEt9Kprhi/ ; quatrième case à gauche Facebook VM Actus et Pronos https://www.facebook.com/share/1KCGttXow1/ ; cinquième case à droite TikTok https://www.tiktok.com/@vmunivers.fr. Il a confirmé que le deuxième lien était bien Facebook. Le reste de la vitrine est conservé. La correction est dans Velocemercato/vmunivers, commit 262e40c324ef3eb8bbd9ca028cb5286433ec4746.','', '## Publications dont les liens sont confirmés','',
           '| Destination | Nombre relevé dans les reçus de cette reprise |','|---|---|']
    for account in names:
        for network in ('facebook','instagram'):
            if account=='meta_pronos' and network=='instagram':continue
            target=account+'/'+network
            count=sum(row['target']==target for row in confirmed.values())
            lines.append(f'| {names[account]} · {network} | {count} |')
    lines += ['', 'Ces nombres comptent les identifiants uniques avec confirmation et URL publique. Un statut programmé, envoi ou workflow réussi ne suffit pas. Les reçus détaillés sont dans studio/editorial-status.json et dans le kit https://velocemercato.fr/studio/kit-automatique.html.', '',
              '## Programme actif et responsabilités','',
              '| Canal | Responsable technique | Objectif demandé |','|---|---|---|',
              '| Facebook Véloce Mercato | editorial-vm.yml, connexion meta | Article Foot ou Multisport toutes les 10 minutes, 24 h/24 |',
              '| Facebook VM Actus | editorial-vm.yml, connexion meta_pronos | Actualités variées toutes les 10 minutes, 24 h/24 |',
              '| Facebook VM Univers | editorial-vm.yml, connexion meta_univers | Un projet chaque heure, 24 h/24 |',
              '| Instagram veloce.mercato | Même circuit, identité vérifiée | Un contenu sport toutes les 15 minutes selon quota |',
              '| Instagram vmunivers.fr | Même circuit, identité vérifiée | Un projet toutes les 15 minutes selon quota |',
              '| Troisième Instagram | Aucun | Identité et connexion à fournir ; aucun envoi vers un compte supposé |',
              '| TikTok @velocemercato | Tâche ChatGPT/Metricool b430a95c… | Trois vidéos par bloc, 9 h / 12 h / 20 h Paris, neuf par jour si disponibles |',
              '| Rendus vidéo | teasers-vm.yml + chaîne des JT existante | Flashes originaux, voix Piper et musique VM, puis ajout au kit |',
              '| YouTube | Workflows existants | Les JT existants sont conservés ; la production de flashes n’ajoute pas neuf uploads YouTube |',
              '| Conseils pronos, choix éditoriaux et validation artistique | Romain | Garder sa maîtrise |', '',
              'Un seul expéditeur TikTok est retenu : la tâche Metricool. Le workflow tiktok-metricool.yml reste un diagnostic privé. Ne pas le réactiver en production en parallèle. Les envois ont un accusé avant l’appel API ; une réponse ambiguë n’est jamais relancée automatiquement. Les anciens circuits d’articles cèdent la main uniquement après confirmation de la connexion du nouveau circuit. Les JT/Reels, campagnes et conseils existants gardent leurs propres reçus.', '',
              'Les cadences sont des objectifs, pas une promesse de remplissage. Les plafonds de rédaction actuels restent 48 brèves Foot, 36 Actus et 16 Gaming par jour, plus les titres Multisport. S’il manque du contenu inédit ou un quota, laisser le créneau vide. GitHub peut retarder ses cron. Les quotas Instagram sont vérifiés au moment des envois.', '',
              '## Sources envoyées par Romain','',
              'Les 30 références sont transcrites dans sources/demandees-romain.json. Les résultats de contrôle sont dans sources/flux-valides.json. Aucune source existante n’a été supprimée. Les ajouts ne sont activés qu’après validation du flux et respect des accès autorisés. L’Équipe, CIES et Reuters demandent une revue éditoriale ou contractuelle ; aucun accès payant n’est contourné. Les titres étrangers nécessitent une rédaction française, sans copie intégrale.', '',
              '| Source | Résultat actuel |','|---|---|']
    for row in sources.get('sources',[]):lines.append('| '+row['name']+' | '+row['status']+' |')
    lines += ['', 'Pour Multisport, les flux français validés Sports.fr et Le Monde Sport sont raccordés. Les autres sources étrangères restent au catalogue pour ajout de la traduction dans la chaîne éditoriale. La dernière lettre isolée « S » de la photo multisport n’a pas été interprétée comme un média.', '',
              '## Audit des pages, liens et classements','',
              f'- Pages HTML examinées : {audit.get("html_pages","en cours")}.',
              f'- URL interrogées : {audit.get("live_urls_checked","en cours")}.',
              f'- HTTP 404/410 confirmés : {len(audit.get("broken_urls_404_410",[]))}.',
              f'- Cibles internes absentes du dépôt : {len(audit.get("local_targets_absent",[]))}.',
              f'- Liens protégés/non vérifiables automatiquement : {len(audit.get("protected_or_unverified_urls",[]))}.',
              f'- Ancres à relire : {len(audit.get("anchors_to_review",[]))}. Certaines existent seulement après chargement JavaScript.',
              f'- Classements à relire : {len(audit.get("classification_to_review",[]))}.', '',
              'Le détail exhaustif des contrôles effectués, avec fichiers et lignes, est dans docs/AUDIT_CLAUDE_2026-11-11.json et son résumé Markdown. Un refus 403/429 ne prouve pas un lien mort. Cet audit ne certifie pas tous les faits d’actualité, la disponibilité géographique des vidéos, les paiements ou les espaces authentifiés.', '',
              '## Vidéos, référence musicale et reste à faire','',
              f'Le dernier rendu répertorie {len(teasers.get("videos",[]))} nouveaux flashes, bloc {teasers.get("planned_for","en cours")}. Lire studio/teasers.json pour les URLs réelles.', '',
              'Lire docs/CLAUDE_VIDEO_VM_2026-11-11.md : référence fournie, storyboard, paroles originales proposées, format de livraison, accès CapCut non vérifié, chant encore à produire et dixième clip promotionnel non programmé. Les neuf créneaux TikTok ne constituent pas neuf confirmations de publication.', '',
              '## Reprise concrète pour Claude','',
              '1. Lire main et ce dossier ; conserver les changements récents des autres assistants. Ne pas faire de restauration globale ni de force-push.',
              '2. Contrôler /foot/ : visuel du 4 novembre, flux du jour, ouverture des articles, filtres, scores, mobile, lisibilité et lien retour. Tester aussi le clic au doigt sur les cadres SVG du bureau : un ancien test de centre géométrique avait ouvert un autre volet, même si le clavier sélectionnait le bon.',
              '3. Corriger les vrais liens morts, puis les cibles internes et ancres réellement manquantes. Lire les références du JSON ; ne pas supprimer un lien protégé sur la seule base de 403/429.',
              '4. Relire les articles signalés, notamment un ancien One Piece mal placé dans Gaming. Le filtre Multisport exclut les jeux vidéo et ne charge plus les brèves Foot. Vérifier les cartes anciennes de type Coupe du monde de rugby 2023 dont un RSS annonce une date récente.',
              '5. Vérifier les réservations et URLs de chaque réseau avant toute action ; ne pas remplacer la clé de l’état chiffré, ni effacer les reçus pour recommencer un lot.',
              '6. Identifier le troisième Instagram avec Romain et vérifier son droit de publication avant de le raccorder. Les deux identités confirmées sont veloce.mercato et vmunivers.fr.',
              '7. Améliorer les nouvelles animations et produire le refrain chanté original, puis le dixième clip promotionnel. Vérifier les propres accès de Claude à Metricool, GitHub et, si nécessaire, CapCut. Ne pas annoncer un accès hérité de ChatGPT.',
              '8. Refaire les tests concernés, publier via deployer-accueil-cloudflare.yml, contrôler le domaine public et actualiser ce dossier à partir des reçus.', '',
              '## Liens des publications confirmées','']
    for row in sorted(confirmed.values(),key=lambda x:(x['target'],x.get('title',''))):lines.append('- '+row['target']+' — '+row.get('title','Publication VM')+' — '+row['url'])
    path=ROOT/'docs/DOSSIER_CLAUDE_VM_2026-11-11.md'
    path.parent.mkdir(exist_ok=True)
    path.write_text('\n'.join(lines)+'\n')
    print('Dossier Claude actualisé :',len(confirmed),'confirmations uniques.')


if __name__=='__main__':main()
