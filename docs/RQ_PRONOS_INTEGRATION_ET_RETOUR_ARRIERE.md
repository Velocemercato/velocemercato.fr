# RQ Pronos — intégration prudente, 31 octobre 2026

## État actuel
- Page : **112294796981981**, variable GitHub Actions `VM_FACEBOOK_PRONOS_PAGE_ID`.
- Destination nouvelle : `meta_pronos`, exclusivement Facebook (pas d'Instagram).
- Destinations existantes : `meta` (VeloceMercato) et `meta_univers` (VMunivers.fr), non redirigées.
- Le workflow de publication existant `.github/workflows/publier-meta.yml` n'a pas été modifié.
- La publication automatique sur RQ Pronos **n'est pas activée**.
- Aucun jeton n'est demandé en conversation ni inséré dans les fichiers.

## Ordre de validation
1. GitHub → Settings → Secrets and variables → Actions → Variables → ajouter `VM_FACEBOOK_PRONOS_PAGE_ID` avec la valeur `112294796981981`.
2. GitHub Actions → `VM - Connecter Facebook et Instagram` : choisir **pronos**, **dry_run=true**. Le programme consulte `/me/accounts` et échoue si l'ID n'y figure pas. Aucun jeton enregistré, aucune publication.
3. Vérifier que le workflow a réussi et que son diagnostic cite le bon ID. Si les autorisations de cette Page sont insuffisantes, les régler *dans Meta* sans exposer les jetons.
4. Relancer la connexion avec **pronos**, **dry_run=false** seulement après le diagnostic réussi : elle conserve les deux autres connexions.
5. GitHub Actions → `VM - RQ Pronos Facebook (diagnostic et test unique)` : choisir **diagnostic**. Le diagnostic ne publie rien.
6. Après contrôle et accord explicite pour **une** publication publique, activer la variable GitHub `VM_PRONOS_TEST_APPROVED=true`, lancer **test** une seule fois. La réponse doit prouver que l'identifiant commence par l'ID Page et que Meta renvoie une URL `facebook.com` cohérente. En cas d'échec, ne pas relancer à l'aveugle : consulter les accusés chiffrés.
7. Ne pas activer d'automatisation récurrente tant que le test unique et sa visibilité publique ne sont pas confirmés.

## Retour arrière
Le nouveau script `tools/pronos_facebook.py`, son test `tests/test_pronos_meta.py` et le workflow `.github/workflows/pronos-meta.yml` sont indépendants des publications existantes. Les désactiver ou supprimer suffit à stopper les tests RQ Pronos. Ne pas retirer les jetons ou l'état chiffré des deux autres Pages.

Les changements de code réalisés :
- `8b3fe71d79d87e73dda9450677aefa0b25144af2` : sélection stricte des comptes dans `tools/publier_meta.py`.
- `5c3c4c204fc8b79b21db2bdb0bab61559827bd88` : nouveau script RQ Pronos.
- `88a30d3d2e5181cb04611f28be576db8133e8ce8` : workflow manuel RQ Pronos.
- `a19059712f1a7eb2fc5816c6043a1cc03bc51a08` : tests hors ligne.
- `6319e957c7b9a807e9c5f43723b8aa0ed4b8a4f5` : workflow de connexion ciblé.

Ne pas réinitialiser la branche `broadcast-state` ni le secret `VM_DIFFUSION_STATE_KEY` : ils conservent les accusés et les connexions existantes. Pour revenir à la version de connexion précédente, restaurer les fichiers ciblés depuis leurs versions Git antérieures et vérifier que `meta` et `meta_univers` restent inchangés.

## Contenus
La bibliothèque actuelle propose la sélection foot, actus, Belfort, gaming, JT, projet VM Univers (une sélection quotidienne), pronostic si disponible et suffisamment récent. Un seul pronostic est effectivement disponible dans `prono.json` : aucun deuxième n'est inventé.
Aucune montante réelle, aucun gain promis. Mention obligatoire : « Jouer comporte des risques, 18+, Joueurs Info Service 09 74 75 13 13 ».
Les développements ultérieurs d'une programmation récurrente restent à valider séparément.
