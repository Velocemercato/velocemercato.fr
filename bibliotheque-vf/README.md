# Bibliothèque VF (dossier ChatGPT du 4/11/2026)

| Fichier | Rôle |
|---|---|
| `candidats.json` | 436 œuvres de l'inventaire, **toutes au statut `candidat`**, audio `VF_A_VERIFIER`. Rien n'est inventé. Régénérer avec `python tools/bibliotheque_vf_candidats.py`. |
| `liens.json` | Les liens YouTube à contrôler, avec la chaîne attendue (identifiant ou handle quand il est connu). `publie` = page VM déjà en ligne ; `candidat` = trouvé par recherche, non vérifié. |
| `verifications.json` | Journal écrit chaque matin par `tools/verifier_vf.py` (workflow `vm-bibliotheque-vf.yml`) : date, chaîne, preuve, audio, France, intégration, qualité, statut. |

## Statuts
- **verifie** : chaîne officielle prouvée par son identifiant, vidéo lisible, France autorisée, VF prouvée. Seuls ces liens apparaissent sur https://velocemercato.fr/mangas/vf/.
- **candidat** : au moins une preuve manque (le motif est écrit).
- **retire** : vidéo supprimée ou introuvable. Si une page VM est en ligne, une alerte `::warning::` la signale (pas de suppression automatique).
- **non_controle** : YouTube injoignable ce jour-là, aucune conclusion.

## Preuve de la VF
1. une piste audio française déclarée par YouTube ; ou
2. la VF / le français annoncé dans le titre par la chaîne officielle prouvée ; ou
3. la chaîne officielle prouvée est l'édition française déclarée (`"francophone": true`, avec la page de la chaîne en preuve).

Un titre en français ne suffit pas, et « VOSTFR » / « sous-titré » donne `PAS_DE_VF`.

## Limites
- Le contrôle lit seulement les métadonnées publiques. Il ne télécharge et n'écoute aucune vidéo. Pour les cas `VF_A_VERIFIER`, une écoute humaine reste nécessaire.
- L'accès depuis la France est lu dans la liste des pays de la page publique YouTube. Si elle est absente, il reste « inconnu ».
- France TV, ARTE, TF1, M6+, Pluto TV, ADN, Crunchyroll et les plateformes payantes n'ont pas d'API publique de ce type. Ils restent en lien direct « à vérifier » chez le diffuseur.
- **Aucune rubrique adulte** : South Park, Les Griffin, American Dad! et Rick et Morty sont marqués `adulte` et exclus. Les contenus pornographiques sont exclus (contrôle d'âge Arcom requis, audit juridique préalable).
