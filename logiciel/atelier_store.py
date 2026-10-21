"""VM Performance 2.0 — gestion atelier (sans interface) : clients, véhicules,
interventions/devis, journal de recharge, sauvegarde/restauration, exports.

Données stockées UNIQUEMENT en local (SQLite). Collecte minimale : pas de pièce
d'identité, pas de code de sécurité, pas de mot de passe constructeur.
"""
from __future__ import annotations

import csv
import os
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, date
from pathlib import Path

SCHEMA_VERSION = 1
TYPES_VEHICULE = ("Auto", "Moto", "Utilitaire")
ENERGIES = ("Essence", "Diesel", "Hybride", "Électrique", "E85 / Flex", "GPL", "Autre")
TYPES_INTERVENTION = ("Diagnostic", "Dossier clé", "Étude Stage 1 / E85", "Véhicule électrique", "Entretien", "Autre")
STATUTS = ("Devis", "Accepté", "En cours", "Terminé", "Facturé", "Annulé")

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS meta (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS clients (
  id TEXT PRIMARY KEY, nom TEXT NOT NULL, telephone TEXT NOT NULL DEFAULT '',
  email TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '', cree TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS vehicules (
  id TEXT PRIMARY KEY, client_id TEXT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  type TEXT NOT NULL, marque TEXT NOT NULL, modele TEXT NOT NULL DEFAULT '', annee TEXT NOT NULL DEFAULT '',
  energie TEXT NOT NULL, kilometrage INTEGER, cree TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS interventions (
  id TEXT PRIMARY KEY, vehicule_id TEXT NOT NULL REFERENCES vehicules(id) ON DELETE CASCADE,
  date TEXT NOT NULL, type TEXT NOT NULL, description TEXT NOT NULL, montant REAL,
  statut TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0, cree TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS recharges (
  id TEXT PRIMARY KEY, vehicule_id TEXT NOT NULL REFERENCES vehicules(id) ON DELETE CASCADE,
  date TEXT NOT NULL, soc_debut REAL, soc_fin REAL, kwh REAL, temperature REAL, source TEXT NOT NULL, cree TEXT NOT NULL);
"""


class ValidationError(ValueError):
    pass


def default_database() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    folder = Path(base) / "VMPerformance" if base else Path.home() / ".local" / "share" / "VMPerformance"
    return folder / "atelier_v2.sqlite3"


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def csv_safe(value) -> str:
    value = "" if value is None else str(value)
    if value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")) or value[:1] in ("\t", "\r", "\n"):
        return "'" + value
    return value


def _txt(value, name, maxlen=200, required=False) -> str:
    value = (value or "").strip()
    if required and not value:
        raise ValidationError(f"{name} est obligatoire.")
    if len(value) > maxlen:
        raise ValidationError(f"{name} : {maxlen} caractères maximum.")
    return value


def _num(value, name, lo=None, hi=None, integer=False):
    if value in (None, ""):
        return None
    try:
        v = float(str(value).replace(",", ".").replace(" ", ""))
    except ValueError as exc:
        raise ValidationError(f"{name} doit être un nombre.") from exc
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValidationError(f"{name} doit être entre {lo} et {hi}.")
    return int(v) if integer else round(v, 2)


def _date(value, name="Date") -> str:
    value = (value or "").strip() or date.today().isoformat()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValidationError(f"{name} invalide (format JJ/MM/AAAA).")


def _choice(value, name, options) -> str:
    if value not in options:
        raise ValidationError(f"{name} : choix invalide.")
    return value


class Atelier:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else default_database()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._db()) as db:
            db.executescript(SCHEMA)
            db.execute("INSERT OR IGNORE INTO meta VALUES ('schema', ?)", (str(SCHEMA_VERSION),))
            db.commit()

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        return db

    def _exec(self, sql, args=()):
        with closing(self._db()) as db:
            cur = db.execute(sql, args)
            db.commit()
            return cur.rowcount

    def _all(self, sql, args=()):
        with closing(self._db()) as db:
            return [dict(r) for r in db.execute(sql, args).fetchall()]

    # Clients ------------------------------------------------------------
    def ajouter_client(self, nom, telephone="", email="", notes="") -> str:
        nom = _txt(nom, "Nom", 120, True)
        telephone = _txt(telephone, "Téléphone", 30)
        if telephone and not all(c.isdigit() or c in " +.-()" for c in telephone):
            raise ValidationError("Téléphone : chiffres uniquement.")
        email = _txt(email, "E-mail", 120)
        if email and ("@" not in email or "." not in email.split("@")[-1]):
            raise ValidationError("E-mail invalide.")
        cid = uuid.uuid4().hex
        self._exec("INSERT INTO clients VALUES (?,?,?,?,?,?)", (cid, nom, telephone, email, _txt(notes, "Notes", 1000), now()))
        return cid

    def clients(self):
        return self._all("SELECT * FROM clients ORDER BY nom COLLATE NOCASE")

    def supprimer_client(self, cid) -> int:
        """Droit à l'effacement : supprime le client, ses véhicules, interventions et recharges."""
        return self._exec("DELETE FROM clients WHERE id=?", (cid,))

    # Véhicules ----------------------------------------------------------
    def ajouter_vehicule(self, client_id, type_, marque, modele="", annee="", energie="Essence", kilometrage=None) -> str:
        if not self._all("SELECT id FROM clients WHERE id=?", (client_id,)):
            raise ValidationError("Client introuvable.")
        annee = _txt(str(annee or ""), "Année", 4)
        if annee and (not annee.isdigit() or not 1950 <= int(annee) <= date.today().year + 1):
            raise ValidationError("Année invalide.")
        vid = uuid.uuid4().hex
        self._exec("INSERT INTO vehicules VALUES (?,?,?,?,?,?,?,?,?)",
                   (vid, client_id, _choice(type_, "Type", TYPES_VEHICULE), _txt(marque, "Marque", 60, True),
                    _txt(modele, "Modèle", 80), annee, _choice(energie, "Énergie", ENERGIES),
                    _num(kilometrage, "Kilométrage", 0, 2_000_000, True), now()))
        return vid

    def vehicules(self, client_id=None):
        sql = ("SELECT v.*, c.nom AS client FROM vehicules v JOIN clients c ON c.id=v.client_id"
               + (" WHERE v.client_id=?" if client_id else "") + " ORDER BY c.nom, v.marque")
        return self._all(sql, (client_id,) if client_id else ())

    # Interventions ------------------------------------------------------
    def ajouter_intervention(self, vehicule_id, type_, description, montant=None, statut="Devis", date_=None, demo=False) -> str:
        if not self._all("SELECT id FROM vehicules WHERE id=?", (vehicule_id,)):
            raise ValidationError("Véhicule introuvable.")
        iid = uuid.uuid4().hex
        self._exec("INSERT INTO interventions VALUES (?,?,?,?,?,?,?,?,?)",
                   (iid, vehicule_id, _date(date_), _choice(type_, "Type", TYPES_INTERVENTION),
                    _txt(description, "Description", 2000, True), _num(montant, "Montant", 0, 100000),
                    _choice(statut, "Statut", STATUTS), 1 if demo else 0, now()))
        return iid

    def changer_statut(self, iid, statut) -> int:
        return self._exec("UPDATE interventions SET statut=? WHERE id=?", (_choice(statut, "Statut", STATUTS), iid))

    def interventions(self, vehicule_id=None):
        sql = ("SELECT i.*, v.marque, v.modele, c.nom AS client FROM interventions i "
               "JOIN vehicules v ON v.id=i.vehicule_id JOIN clients c ON c.id=v.client_id"
               + (" WHERE i.vehicule_id=?" if vehicule_id else "") + " ORDER BY i.date DESC, i.cree DESC")
        return self._all(sql, (vehicule_id,) if vehicule_id else ())

    # Recharges (véhicules électriques) ----------------------------------
    def ajouter_recharge(self, vehicule_id, date_=None, soc_debut=None, soc_fin=None, kwh=None, temperature=None, source="Saisie manuelle") -> str:
        if not self._all("SELECT id FROM vehicules WHERE id=?", (vehicule_id,)):
            raise ValidationError("Véhicule introuvable.")
        d, f = _num(soc_debut, "Charge début (%)", 0, 100), _num(soc_fin, "Charge fin (%)", 0, 100)
        if d is not None and f is not None and f < d:
            raise ValidationError("La charge de fin doit être supérieure ou égale à celle du début.")
        rid = uuid.uuid4().hex
        self._exec("INSERT INTO recharges VALUES (?,?,?,?,?,?,?,?,?)",
                   (rid, vehicule_id, _date(date_), d, f, _num(kwh, "Énergie (kWh)", 0, 500),
                    _num(temperature, "Température (°C)", -40, 80), _txt(source, "Source", 60, True), now()))
        return rid

    def recharges(self, vehicule_id):
        return self._all("SELECT * FROM recharges WHERE vehicule_id=? ORDER BY date DESC", (vehicule_id,))

    # Sauvegarde / restauration / conservation ---------------------------
    def sauvegarder(self, destination: Path) -> Path:
        destination = Path(destination)
        with closing(self._db()) as src, closing(sqlite3.connect(destination)) as dst:
            src.backup(dst)
        return destination

    def restaurer(self, source: Path) -> None:
        source = Path(source)
        try:
            with closing(sqlite3.connect(f"file:{source}?mode=ro", uri=True)) as db:
                tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                ok = db.execute("PRAGMA integrity_check").fetchone()[0]
        except sqlite3.DatabaseError as exc:
            raise ValidationError("Ce fichier n'est pas une sauvegarde VM Performance valide.") from exc
        if not {"clients", "vehicules", "interventions", "meta"} <= tables or ok != "ok":
            raise ValidationError("Ce fichier n'est pas une sauvegarde VM Performance valide.")
        with closing(sqlite3.connect(source)) as src, closing(sqlite3.connect(self.path)) as dst:
            src.backup(dst)
        with closing(self._db()) as db:
            db.executescript(SCHEMA)

    def purger_anciens(self, annees: int = 3) -> int:
        """Supprime les clients sans intervention depuis `annees` ans (durée de conservation)."""
        limite = date(date.today().year - annees, date.today().month, min(date.today().day, 28)).isoformat()
        anciens = self._all("SELECT c.id FROM clients c WHERE c.cree < ? AND NOT EXISTS ("
                            "SELECT 1 FROM interventions i JOIN vehicules v ON v.id=i.vehicule_id "
                            "WHERE v.client_id=c.id AND i.date >= ?)", (limite, limite))
        for row in anciens:
            self.supprimer_client(row["id"])
        return len(anciens)

    # Exports -------------------------------------------------------------
    def export_csv(self, path: Path) -> Path:
        rows = self.interventions()
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(["Date", "Client", "Véhicule", "Type", "Description", "Montant (€)", "Statut", "Données"])
            for r in rows:
                w.writerow([r["date"], csv_safe(r["client"]), csv_safe(f"{r['marque']} {r['modele']}".strip()),
                            r["type"], csv_safe(r["description"]),
                            "" if r["montant"] is None else f"{r['montant']:.2f}".replace(".", ","),
                            r["statut"], "DÉMO" if r["demo"] else "Réelle"])
        return Path(path)

    def rapport_lignes(self, vehicule_id) -> tuple[str, list[str]]:
        v = next((x for x in self.vehicules() if x["id"] == vehicule_id), None)
        if not v:
            raise ValidationError("Véhicule introuvable.")
        titre = f"Fiche atelier — {v['marque']} {v['modele']}".strip()
        lignes = ["# Client et véhicule", f"Client : {v['client']}",
                  f"Véhicule : {v['type']} {v['marque']} {v['modele']} {v['annee']}".strip(),
                  f"Énergie : {v['energie']}" + (f" · {v['kilometrage']} km" if v["kilometrage"] is not None else ""),
                  "# Interventions"]
        inter = self.interventions(vehicule_id)
        if not inter:
            lignes.append("Aucune intervention enregistrée.")
        for i in inter:
            m = "" if i["montant"] is None else f" — {i['montant']:.2f} €".replace(".", ",")
            lignes.append(f"{i['date']} · {i['type']} · {i['statut']}{m}" + (" · [DONNÉES DE DÉMONSTRATION]" if i["demo"] else ""))
            lignes.append(f"   {i['description']}")
        rec = self.recharges(vehicule_id)
        if rec:
            lignes.append("# Journal de recharge")
            for r in rec:
                lignes.append(f"{r['date']} · {r['soc_debut'] if r['soc_debut'] is not None else '?'} % → "
                              f"{r['soc_fin'] if r['soc_fin'] is not None else '?'} % · "
                              f"{r['kwh'] if r['kwh'] is not None else '?'} kWh · "
                              f"{r['temperature'] if r['temperature'] is not None else '?'} °C · {r['source']}")
        lignes += ["", "Document généré localement par VM Performance 2.0 (prototype). "
                   "Ne remplace pas un diagnostic constructeur."]
        return titre, lignes
