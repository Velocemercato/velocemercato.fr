"""VM Performance 2.0 — Étude Stage 1 / E85 : SIMULATION ET ANALYSE UNIQUEMENT.

Aucune lecture ni écriture de calculateur. Les courbes sont des formes
génériques construites à partir des valeurs saisies par l'utilisateur
(fiche constructeur, banc de puissance, devis du préparateur) : elles sont
toujours annotées « estimation non certifiée ».
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import math

AVERTISSEMENT = ("ESTIMATION NON CERTIFIÉE — courbes indicatives générées à partir des valeurs saisies. "
                 "Ce n'est ni une mesure au banc, ni une reprogrammation. Toute modification des performances "
                 "peut nécessiter une mise en conformité (homologation / certificat d'immatriculation), "
                 "doit être déclarée à l'assureur et peut affecter la garantie et le contrôle technique.")

CHECKLIST_E85 = (
    ("homologue", "Boîtier de conversion E85 homologué pour ce modèle (liste officielle, pas un boîtier générique)"),
    ("installateur", "Pose par un installateur agréé par le fabricant du boîtier"),
    ("carte_grise", "Mise à jour du certificat d'immatriculation (mention carburant) prévue"),
    ("assurance", "Assureur prévenu de la modification"),
    ("moteur", "Moteur essence compatible selon le fabricant du boîtier (injection, cylindrée, norme Euro)"),
    ("entretien", "Entretien à jour (bougies, filtre, injecteurs) avant conversion"),
    ("pompe", "Station E85 accessible près de chez le client"),
)

CHECKLIST_STAGE1 = (
    ("etat", "Diagnostic préalable sans défaut (codes lus et moteur sain)"),
    ("entretien", "Entretien à jour, embrayage et refroidissement en bon état"),
    ("antipollution", "AUCUNE suppression ou désactivation d'antipollution (FAP, EGR, AdBlue, catalyseur) : interdit"),
    ("conformite", "Démarche de conformité étudiée (réception à titre isolé, certificat d'immatriculation)"),
    ("assurance", "Assureur informé, garantie constructeur vérifiée"),
    ("pro", "Intervention réalisée par un professionnel équipé et autorisé — pas par ce logiciel"),
)


class EtudeErreur(ValueError):
    pass


@dataclass
class Moteur:
    puissance_ch: float
    couple_nm: float
    regime_couple: int = 2500
    regime_puissance: int = 5500
    regime_max: int = 6500

    def valider(self):
        if not 20 <= self.puissance_ch <= 1500:
            raise EtudeErreur("Puissance : entre 20 et 1500 ch.")
        if not 30 <= self.couple_nm <= 2500:
            raise EtudeErreur("Couple : entre 30 et 2500 Nm.")
        if not 800 <= self.regime_couple < self.regime_puissance <= self.regime_max <= 12000:
            raise EtudeErreur("Régimes : couple max < puissance max ≤ régime maxi (≤ 12 000 tr/min).")


def courbe(m: Moteur, pas: int = 250) -> list[tuple[int, float, float]]:
    """Forme générique : couple qui monte jusqu'au régime de couple max, plateau,
    puis décroissance calée pour que la puissance culmine à la valeur saisie.
    Retourne [(tr/min, couple Nm, puissance ch)]."""
    m.valider()
    debut = 1000
    t_at_p = m.puissance_ch * 7023.5 / m.regime_puissance  # couple nécessaire au régime de puissance max
    t_at_p = min(t_at_p, m.couple_nm)
    pts = []
    for rpm in range(debut, m.regime_max + 1, pas):
        if rpm <= m.regime_couple:
            x = (rpm - debut) / max(1, m.regime_couple - debut)
            t = m.couple_nm * (0.62 + 0.38 * math.sin(x * math.pi / 2))
        elif rpm <= m.regime_puissance:
            x = (rpm - m.regime_couple) / max(1, m.regime_puissance - m.regime_couple)
            t = m.couple_nm + (t_at_p - m.couple_nm) * x * x
        else:
            x = (rpm - m.regime_puissance) / max(1, m.regime_max - m.regime_puissance)
            t = t_at_p * (1 - 0.18 * x)
        pts.append((rpm, round(t, 1), round(t * rpm / 7023.5, 1)))
    return pts


@dataclass
class Etude:
    nom: str
    origine: Moteur
    cible: Moteur
    checklist: dict = field(default_factory=dict)
    source_cible: str = ""

    def ecarts(self) -> dict:
        o, c = self.origine, self.cible
        return {
            "puissance_ch": round(c.puissance_ch - o.puissance_ch, 1),
            "puissance_pct": round((c.puissance_ch / o.puissance_ch - 1) * 100, 1),
            "couple_nm": round(c.couple_nm - o.couple_nm, 1),
            "couple_pct": round((c.couple_nm / o.couple_nm - 1) * 100, 1),
        }

    def alertes(self) -> list[str]:
        e = self.ecarts()
        out = []
        if not self.source_cible.strip():
            out.append("Valeurs « après » sans source : indique d'où elles viennent (banc, préparateur, fiche).")
        if e["puissance_pct"] > 35 or e["couple_pct"] > 40:
            out.append("Gain annoncé très élevé pour un « Stage 1 » : à vérifier sérieusement avant toute promesse au client.")
        if e["puissance_pct"] < 0 or e["couple_pct"] < 0:
            out.append("Valeurs « après » inférieures à l'origine : vérifier la saisie.")
        return out

    def lignes_rapport(self) -> list[str]:
        e = self.ecarts()
        lignes = [f"# Étude « {self.nom} »", AVERTISSEMENT, "",
                  f"Origine : {self.origine.puissance_ch:g} ch / {self.origine.couple_nm:g} Nm",
                  f"Après (valeurs saisies) : {self.cible.puissance_ch:g} ch / {self.cible.couple_nm:g} Nm",
                  f"Source des valeurs « après » : {self.source_cible or 'NON RENSEIGNÉE'}",
                  f"Écart : {e['puissance_ch']:+g} ch ({e['puissance_pct']:+g} %) · {e['couple_nm']:+g} Nm ({e['couple_pct']:+g} %)"]
        if self.alertes():
            lignes.append("# Alertes")
            lignes += [f"⚠ {a}" for a in self.alertes()]
        lignes.append("# Points de contrôle")
        for k, txt in CHECKLIST_STAGE1 + CHECKLIST_E85:
            lignes.append(f"[{'X' if self.checklist.get(k) else ' '}] {txt}")
        lignes.append("# Courbes indicatives (tr/min : couple origine → après · puissance origine → après)")
        for (r, t0, p0), (_, t1, p1) in zip(courbe(self.origine, 500), courbe(self.cible, 500)):
            lignes.append(f"{r:>5} tr/min : {t0:g} → {t1:g} Nm · {p0:g} → {p1:g} ch")
        return lignes

    def to_json(self) -> str:
        return json.dumps({"nom": self.nom, "origine": self.origine.__dict__, "cible": self.cible.__dict__,
                           "checklist": self.checklist, "source_cible": self.source_cible}, ensure_ascii=False)

    @classmethod
    def from_json(cls, txt: str) -> "Etude":
        d = json.loads(txt)
        return cls(d["nom"], Moteur(**d["origine"]), Moteur(**d["cible"]), d.get("checklist", {}), d.get("source_cible", ""))


def score_checklist(checklist: dict, items) -> tuple[int, int]:
    return sum(1 for k, _ in items if checklist.get(k)), len(items)
