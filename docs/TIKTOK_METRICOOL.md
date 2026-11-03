# JT La Pastille TV → TikTok via Metricool

Workflow : **« VM - JT vers TikTok (Metricool) »** (`.github/workflows/tiktok-metricool.yml`), script `tools/tiktok_metricool.py`.
Aucun robot existant n'est modifié : le script lit les verticales produites par « VM - Kit réseaux des JT ».

## Ce que fait la chaîne
1. Prend le JT le plus ancien des dernières 30 h (univers `foot` par défaut, 1 par passage) pas encore traité.
2. Télécharge sa verticale, la convertit en **1080×1920, H.264/AAC, 30 i/s**, refuse toute vidéo muette ou non conforme.
3. L'héberge sur la branche technique `tiktok` (lien jsDelivr figé, comme le kit réseaux).
4. Crée la publication dans Metricool avec l'**API officielle** (`POST /api/v2/scheduler/posts`, en-tête `X-Mc-Auth`) :
   - **mode essai** : *brouillon* Metricool, visibilité « moi uniquement » → **rien n'est publié** ;
   - **mode publier** : programmée à +15 min, publique, publication automatique par Metricool.
5. Accusé chiffré (branche `tiktok-state`) écrit **avant** l'envoi : un JT envoyé à Metricool n'est **jamais renvoyé** ;
   un échec avant l'envoi (téléchargement, conversion) est retenté 3 fois au plus. Journal lisible : `studio/tiktok.json`.
6. « Programmé » n'est pas « publié » : la publication réelle se vérifie dans Metricool ou sur TikTok.

## Mise en route (Heineguez, une seule fois)
1. **Vérifier l'offre Metricool** : l'API est réservée aux offres **Advanced / Custom** (selon Metricool ; à confirmer dans
   Metricool → Facturation). Le connecteur ChatGPT ne peut pas être utilisé depuis GitHub.
2. Dans Metricool → **Paramètres du compte → API** : copier le **jeton d'API** et l'**identifiant utilisateur** ;
   l'**identifiant de marque** (blogId) de « velocemercato » figure dans l'adresse de la marque (`blogId=…`).
3. Dans GitHub → *Settings → Secrets and variables → Actions* → **New repository secret**, créer trois **nouveaux** secrets :
   `METRICOOL_USER_TOKEN`, `METRICOOL_USER_ID`, `METRICOOL_BLOG_ID` (aucun secret existant n'est touché).
4. **Essai** : *Actions → VM - JT vers TikTok (Metricool) → Run workflow → essai*. Un brouillon apparaît dans le planificateur
   Metricool. Vérifier la vidéo (format, son, lisibilité) et le texte.
5. **Activer** : *Variables → New repository variable* `VM_AUTO_TIKTOK` = `true`. Dès lors, après chaque kit réseaux,
   **1 JT Foot** est programmé. Pour ajouter d'autres JT plus tard : variable `VM_TIKTOK_UNIVERS` = `foot,actus,gaming`.
   **Arrêt** : supprimer `VM_AUTO_TIKTOK` (ou la mettre à `false`).

## Points à valider avant d'activer
- **Sous-titres** : les répliques s'affichent dans les bulles de l'image du JT, mais **en petit** sur téléphone. Le texte
  exact n'est pas conservé hors du robot de production. Pour de grands sous-titres fiables, il faudrait que le robot des JT
  enregistre ses répliques minutées (petit ajout dans `update_debat.py`) : **modification d'un robot existant, à autoriser
  séparément**. Une transcription automatique (reconnaissance vocale) est possible mais risque d'erreurs sur les noms.
- **Musique de fond** `studio/assets/beat.m4a` : fichier ajouté le 20 octobre avec le générateur des émissions, produit par
  ffmpeg ; son origine n'est pas documentée. À confirmer comme création VM avant une diffusion large sur TikTok.
- **Contenu IA** : la légende indique « JT généré par IA, présentateur virtuel ». Activer aussi l'étiquette « Contenu généré
  par IA » de TikTok si Metricool la propose pour la publication.
- Le texte TikTok passe sur une seule ligne (l'API TikTok ne gère pas les retours à la ligne) et reste sous 2 000 caractères.
