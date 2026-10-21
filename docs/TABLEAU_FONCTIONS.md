# VM Performance 2.0 — état réel de chaque fonction

| Fonction | État | Preuve / limite |
|---|---|---|
| Mode démo complet sans véhicule | ✅ Opérationnel | Selftest automatique de l'EXE sur Windows (GitHub Actions) |
| Lecture OBD2 mode 01 (régime, vitesse, T°, charge, tension) | 🟡 Codé, **non testé sur véhicule** | Via python-OBD 0.7.3 ; à valider avec un adaptateur et un véhicule autorisé |
| Lecture des codes défaut (mode 03) | 🟡 Codé, non testé sur véhicule | Lecture seule, pas d'effacement |
| Identification VIN | ⛔ Non développé | Prévu en 2.1 (mode 09), à tester véhicule par véhicule |
| Graphique + export CSV des mesures | ✅ Opérationnel | — |
| Dossiers clés (administratif) | ✅ Opérationnel | Tests unitaires ; **aucune programmation réelle** (outils agréés hors logiciel, accès SERMI) |
| Atelier : clients, véhicules, devis, statuts | ✅ Opérationnel | Tests unitaires (validation, cascade, neutralisation CSV) |
| Fiche PDF / export CSV atelier | ✅ Opérationnel | PDF généré sans dépendance, testé |
| Sauvegarde / restauration / purge 3 ans | ✅ Opérationnel | Tests unitaires (dont fichier invalide refusé) |
| Stage 1 / E85 | 🔵 **Simulation uniquement** | Courbes génériques + écarts + alertes + checklist ; mention « estimation non certifiée » partout |
| Écriture / reprogrammation calculateur | ⛔ Volontairement absent | Interdit dans cette version |
| Électrique : données OBD standard | 🟡 Codé, non testé sur véhicule | Beaucoup de VE ne fournissent PAS ces PID en OBD standard |
| Santé batterie (SoH) | ⛔ Non disponible | Nécessite l'outil/API officielle du constructeur |
| Journal de recharge | ✅ Opérationnel (saisie manuelle) | — |
| Signature de l'EXE / installateur | ⛔ Non fait | Certificat de signature de code à acheter si diffusion pro |
