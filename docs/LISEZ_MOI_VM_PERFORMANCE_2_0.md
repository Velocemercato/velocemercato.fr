# VM Performance 2.0 — prototype privé (Windows 10/11)

Logiciel local de **diagnostic OBD2 en lecture seule** et de **gestion d'atelier**.
Romain Oriez — Véloce Web Studio / Groupe VM. Licence GPL-2.0 (compatibilité python-OBD).

## Démarrer
1. Double-clique sur `VM_Performance_2_0.exe` (Windows peut afficher « application non reconnue » : *Informations complémentaires → Exécuter quand même* ; l'EXE n'est pas encore signé).
2. Laisse « Démo » et clique **Simuler les mesures** : tout fonctionne sans véhicule, avec des valeurs **fictives** clairement marquées.
3. Pour un vrai véhicule : branche un adaptateur compatible (voir `MATERIEL.md`), contact mis, moteur à l'arrêt ou au ralenti à l'arrêt, choisis « OBD2 réel », indique le port COM si besoin.

## Les modules
| Bouton | Ce que ça fait |
|---|---|
| Écran principal | Régime, vitesse, température, charge, tension + lecture des codes défaut (lecture seule, pas d'effacement) + export CSV |
| 🔑 Clés / dépannage | Dossiers administratifs : justificatifs de propriété/mandat (déclaratif), étapes, prestataire habilité, rapport. **Aucune programmation de clé.** |
| 🧾 Atelier & devis | Clients, véhicules, devis/interventions, statuts, fiche PDF, export CSV, sauvegarde/restauration, purge > 3 ans |
| 📈 Stage 1 / E85 | Étude **SIMULÉE** : courbes indicatives à partir de valeurs saisies + checklist de conformité. **Aucune écriture calculateur.** |
| ⚡ Électrique / hybride | Lecture des données OBD standard **si le véhicule les fournit** (sinon « non fournie ») + journal de recharge |

Données : `%LOCALAPPDATA%\VMPerformance\` (uniquement sur le PC). Sauvegarde : bouton 💾 dans l'Atelier.
