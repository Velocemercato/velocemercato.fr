"""VM Performance 2.0 — Véhicules électriques et hybrides : lecture OBD standard UNIQUEMENT.

Le protocole OBD2 standard ne donne que peu d'informations sur les batteries de
traction. On n'affiche une valeur QUE si le véhicule la fournit réellement ;
sinon « non fournie par le véhicule ». Aucune estimation déguisée en mesure.
Aucune intervention haute tension : réservée aux personnes habilitées.
"""
from __future__ import annotations

import math
import time

# (clé, libellé, nom de commande python-OBD, unité de conversion, unité affichée)
MESURES_EV = (
    ("batterie_hybride", "Charge batterie hybride/traction (PID 01 5B)", "HYBRID_BATTERY_REMAINING", "percent", "%"),
    ("tension_module", "Tension du calculateur (PID 01 42)", "CONTROL_MODULE_VOLTAGE", "volt", "V"),
    ("temp_air", "Température extérieure (PID 01 46)", "AMBIANT_AIR_TEMP", "degC", "°C"),
    ("vitesse", "Vitesse (PID 01 0D)", "SPEED", "kph", "km/h"),
    ("distance_defaut", "Distance depuis effacement des défauts (PID 01 31)", "DISTANCE_SINCE_DTC_CLEAR", "km", "km"),
)

AVERTISSEMENT_HT = ("⚡ Haute tension : aucune intervention sur la batterie, les câbles orange ou les composants "
                    "haute tension sans habilitation électrique adaptée (B1VL/B2VL/BCL selon l'intervention) "
                    "et procédure constructeur. Ce logiciel ne fait que LIRE les données standard.")

NON_FOURNI = "non fournie par le véhicule"


class DemoEV:
    nom = "DÉMONSTRATION — valeurs simulées (aucun véhicule)"
    demo = True

    def __init__(self):
        self.t0 = time.monotonic()

    def lire(self) -> dict:
        t = time.monotonic() - self.t0
        return {"batterie_hybride": round(62 + 3 * math.sin(t / 30), 1), "tension_module": round(13.6 + 0.1 * math.sin(t / 7), 2),
                "temp_air": 14.0, "vitesse": 0.0, "distance_defaut": 1240.0}


class OBDEV:
    """Lecture seule via une connexion python-OBD déjà ouverte (aucune commande d'écriture)."""
    nom = "OBD2 RÉEL — lecture seule"
    demo = False

    def __init__(self, connexion, module_obd, verrou=None):
        self.conn = connexion
        self.obd = module_obd
        self.verrou = verrou

    def lire(self) -> dict:
        if self.verrou is None:
            return self._lire()
        with self.verrou:  # la connexion OBD n'est pas partagée entre deux lectures simultanées
            return self._lire()

    def _lire(self) -> dict:
        out = {}
        for cle, _lib, cmd_name, unite, _aff in MESURES_EV:
            cmd = getattr(self.obd.commands, cmd_name, None)
            if cmd is None or not self.conn.supports(cmd):
                out[cle] = None
                continue
            r = self.conn.query(cmd)
            if r is None or r.is_null() or r.value is None:
                out[cle] = None
                continue
            v = r.value
            try:
                if hasattr(v, "to"):
                    v = v.to(unite)
                out[cle] = round(float(getattr(v, "magnitude", v)), 2)
            except (TypeError, ValueError, AttributeError):
                out[cle] = None
        return out


def formater(mesures: dict, demo: bool) -> list[str]:
    lignes = []
    for cle, lib, _c, _u, aff in MESURES_EV:
        v = mesures.get(cle)
        txt = NON_FOURNI if v is None else f"{v:g} {aff}"
        lignes.append(f"{lib} : {txt}" + (" [DÉMO]" if demo and v is not None else ""))
    lignes.append("État de santé (SoH) de la batterie : non disponible en OBD standard — "
                  "nécessite l'outil ou l'API officielle du constructeur.")
    return lignes
