# -*- coding: utf-8 -*-
"""VM Performance 1.2 - Suivi d'un remplacement de clé par filière agréée.

Aucune lecture de PIN, aucun dialogue avec antidémarrage/clé/transpondeur,
aucune génération d'identifiants, aucune commande véhicule : administratif seul.
GPL-2.0-only; Copyright (C) 2026 VM Performance contributors.
"""
from __future__ import annotations

import html
import sqlite3
import webbrowser
from contextlib import contextmanager, closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from dossiers_cles import CaseStore, DARK, PANEL, INK, MUTED, NEON, WARNING, now_utc

TYPES = ('Clé mécanique', 'Clé avec télécommande', 'Clé avec transpondeur', 'Clé mains libres', 'À déterminer')
INTERVENTIONS = ('Clé perdue', 'Clé cassée', 'Clé supplémentaire', 'Télécommande défectueuse', 'À diagnostiquer')
PHASES = (
    'Évaluation',
    'Mandat et justificatifs contrôlés',
    'Clé / référence conforme commandée',
    'Intervention constructeur ou prestataire agréé planifiée',
    'Programmation agréée déclarée réalisée',
    'Essais de fonctionnement déclarés réussis',
    'Clôturé',
    'Annulé',
)

NOTICE = (
    'SUIVI ADMINISTRATIF UNIQUEMENT : aucune clé n’est programmée ici. '
    'La programmation réelle s’effectue hors de VM Performance, avec les droits '
    'et équipements approuvés par le constructeur et, lorsque nécessaire, '
    'les habilitations professionnelles applicables (par exemple SERMI). '
    'Ne jamais saisir PIN, secret, certificat, identifiant constructeur, VIN, '
    'numéro de plaque ou justificatif d’identité dans cette application.'
)


@dataclass
class Replacement:
    dossier_id: str
    type_cle: str = TYPES[-1]
    intervention: str = INTERVENTIONS[-1]
    phase: str = PHASES[0]
    controle_acces_professionnel: bool = False
    outil_constructeur_agree: bool = False
    provenance_cle_conforme: bool = False
    essais_declares: bool = False
    prestataire: str = ''
    note: str = ''
    cree: str = ''
    maj: str = ''


def validate(record: Replacement, dossier) -> None:
    if not dossier or dossier.id != record.dossier_id:
        raise ValueError('Dossier d’intervention introuvable.')
    if record.type_cle not in TYPES or record.intervention not in INTERVENTIONS or record.phase not in PHASES:
        raise ValueError('Valeur inconnue pour la clé, l’intervention ou l’étape.')
    record.prestataire = record.prestataire.strip()
    record.note = record.note.strip()
    if len(record.prestataire) > 80 or len(record.note) > 500:
        raise ValueError('Texte trop long : prestataire (80), notes (500).')
    phase_idx = PHASES.index(record.phase)
    if phase_idx not in (0, len(PHASES)-1):
        if not (dossier.identite_propriete_verifiees and dossier.mandat_signe):
            raise ValueError('Bloqué : justificatifs et mandat du dossier initial non validés.')
    if  phase_idx >= 4 and phase_idx != len(PHASES)-1:
        if not (record.controle_acces_professionnel and record.outil_constructeur_agree and record.provenance_cle_conforme):
            raise ValueError('Bloqué : habilitations, équipement agréé et clé conforme à confirmer.')
    if phase_idx in (5, 6) and not record.essais_declares:
        raise ValueError('Bloqué : attestation des essais finaux requise.')


class ReplacementStore:
    def __init__(self, case_store: CaseStore):
        self.case_store = case_store
        self.db_path = case_store.db_path
        with self._conn() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS remplacements (
                dossier_id TEXT PRIMARY KEY REFERENCES dossiers(id) ON DELETE CASCADE,
                type_cle TEXT NOT NULL, intervention TEXT NOT NULL, phase TEXT NOT NULL,
                controle_acces_professionnel INTEGER NOT NULL, outil_constructeur_agree INTEGER NOT NULL,
                provenance_cle_conforme INTEGER NOT NULL, essais_declares INTEGER NOT NULL,
                prestataire TEXT NOT NULL, note TEXT NOT NULL, cree TEXT NOT NULL, maj TEXT NOT NULL
            )''')
            db.execute('''CREATE TABLE IF NOT EXISTS journal_remplacements (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                dossier_id TEXT NOT NULL REFERENCES dossiers(id) ON DELETE CASCADE,
                horodatage TEXT NOT NULL, avant TEXT NOT NULL, apres TEXT NOT NULL
            )''')

    @contextmanager
    def _conn(self):
        with closing(sqlite3.connect(str(self.db_path), timeout=5)) as db:
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA foreign_keys=ON')
            with db:
                yield db

    def get(self, dossier_id: str) -> Replacement | None:
        with self._conn() as db:
            row = db.execute('SELECT * FROM remplacements WHERE dossier_id = ?', (dossier_id,)).fetchone()
        if not row:
            return None
        data = dict(row)
        for flag in ('controle_acces_professionnel', 'outil_constructeur_agree',
                     'provenance_cle_conforme', 'essais_declares'):
            data[flag] = bool(data[flag])
        return Replacement(**data)

    def save(self, record: Replacement) -> Replacement:
        dossier = self.case_store.get(record.dossier_id)
        validate(record, dossier)
        with self._conn() as db:
            previous = db.execute('SELECT phase, cree FROM remplacements WHERE dossier_id=?',
                                  (record.dossier_id,)).fetchone()
            record.cree = previous['cree'] if previous else now_utc()
            record.maj = now_utc()
            db.execute('''INSERT INTO remplacements (
                dossier_id,type_cle,intervention,phase,controle_acces_professionnel,
                outil_constructeur_agree,provenance_cle_conforme,essais_declares,
                prestataire,note,cree,maj)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(dossier_id) DO UPDATE SET
                type_cle=excluded.type_cle, intervention=excluded.intervention,phase=excluded.phase,
                controle_acces_professionnel=excluded.controle_acces_professionnel,
                outil_constructeur_agree=excluded.outil_constructeur_agree,
                provenance_cle_conforme=excluded.provenance_cle_conforme,
                essais_declares=excluded.essais_declares,
                prestataire=excluded.prestataire,note=excluded.note,maj=excluded.maj''',
                (record.dossier_id, record.type_cle, record.intervention, record.phase,
                 int(record.controle_acces_professionnel), int(record.outil_constructeur_agree),
                 int(record.provenance_cle_conforme), int(record.essais_declares),
                 record.prestataire, record.note, record.cree, record.maj))
            if not previous or previous['phase'] != record.phase:
                db.execute('''INSERT INTO journal_remplacements(dossier_id,horodatage,avant,apres)
                    VALUES(?,?,?,?)''', (record.dossier_id, record.maj,
                                        previous['phase'] if previous else '(création)', record.phase))
        return record

    def log(self, dossier_id: str) -> list[tuple[str, str, str]]:
        with self._conn() as db:
            rows = db.execute('''SELECT horodatage,avant,apres FROM journal_remplacements
                    WHERE dossier_id=? ORDER BY seq ASC''', (dossier_id,)).fetchall()
        return [(r['horodatage'], r['avant'], r['apres']) for r in rows]


def report_html(record: Replacement, log: list[tuple[str,str,str]], marque: str, modele: str) -> str:
    e = lambda value: html.escape(str(value), quote=True)
    rows = [
        ('Référence interne',record.dossier_id), ('Véhicule',f'{marque} {modele}'),
        ('Catégorie de clé',record.type_cle),('Motif',record.intervention),('Suivi',record.phase),
        ('Accès professionnel déclaré conforme','Oui' if record.controle_acces_professionnel else 'Non'),
        ('Équipement constructeur / agréé déclaré','Oui' if record.outil_constructeur_agree else 'Non'),
        ('Provenance de clé conforme déclarée','Oui' if record.provenance_cle_conforme else 'Non'),
        ('Essais réalisés déclarés','Oui' if record.essais_declares else 'Non'),
        ('Prestataire (sans identité personnelle)',record.prestataire),
        ('Notes sans informations sensibles',record.note),('Mis à jour',record.maj),
    ]
    trs = ''.join(f'<tr><th>{e(k)}</th><td>{e(v)}</td></tr>' for k,v in rows)
    trail = ''.join(f'<li>{e(t)} · {e(a)} → {e(b)}</li>' for t,a,b in log)
    return ('''<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>VM — Suivi clé agréée</title>
<style>body{font:15px/1.5 Arial,sans-serif;max-width:800px;margin:35px auto;padding:0 12px;color:#10263a}
tr{border-bottom:1px solid #ddd}table{width:100%;border-collapse:collapse}td,th{padding:10px;text-align:left;vertical-align:top;overflow-wrap:anywhere}
th{width:46%;background:#edf6f1}.warning{padding:12px;background:#fff3d6;border-left:5px solid #de9e20;white-space:pre-wrap}</style>
</head><body><h1>VM Performance — Remplacement de clé (suivi)</h1><table>''' + trs +
            '</table><h2>Historique des étapes</h2><ol>' + trail + '</ol><div class="warning">' +
            e(NOTICE) + '</div><p>Document local de suivi ; aucune certification ni programmation n’est réalisée par VM.</p></body></html>')


class ReplacementWindow(tk.Toplevel):
    def __init__(self, parent, case_store: CaseStore, dossier_id: str):
        super().__init__(parent)
        self.title('VM Performance 1.2 — Remplacement et programmation agréée : suivi')
        self.geometry('870x740')
        self.minsize(740, 670)
        self.configure(bg=DARK)
        self.case_store = case_store
        self.store = ReplacementStore(case_store)
        self.case = case_store.get(dossier_id)
        if self.case is None:
            raise ValueError('Dossier introuvable : enregistre-le avant de commencer.')
        self.record = self.store.get(dossier_id) or Replacement(dossier_id=dossier_id)
        self.kind = tk.StringVar(value=self.record.type_cle)
        self.intervention = tk.StringVar(value=self.record.intervention)
        self.phase = tk.StringVar(value=self.record.phase)
        self.pro = tk.BooleanVar(value=self.record.controle_acces_professionnel)
        self.device = tk.BooleanVar(value=self.record.outil_constructeur_agree)
        self.part = tk.BooleanVar(value=self.record.provenance_cle_conforme)
        self.test = tk.BooleanVar(value=self.record.essais_declares)
        self.prestataire = tk.StringVar(value=self.record.prestataire)
        self.status = tk.StringVar(value='Aucun module antidémarrage connecté : suivi seulement.')
        self._ui()

    def _ui(self):
        cont = tk.Frame(self, bg=DARK, padx=24, pady=18)
        cont.pack(fill='both', expand=True)
        tk.Label(cont, text='VM / REMPLACEMENT DE CLÉ', fg=NEON, bg=DARK,
                 font=('Segoe UI',19,'bold')).pack(anchor='w')
        tk.Label(cont,text=f'Dossier {self.case.id} · {self.case.marque} {self.case.modele} ({self.case.annee or "année non précisée"})',
                 fg=INK,bg=DARK,font=('Segoe UI',11)).pack(anchor='w',pady=(4,7))
        tk.Label(cont,text='Suivi des étapes ; la programmation réelle se fait sur l’outil agréé du professionnel.',
                 fg=WARNING,bg=DARK,font=('Segoe UI',10),wraplength=800,justify='left').pack(anchor='w',pady=(0,12))
        fields = tk.Frame(cont,bg=PANEL,padx=14,pady=12)
        fields.pack(fill='x')
        for label, var, options in [('Type de clé',self.kind,TYPES),('Motif',self.intervention,INTERVENTIONS),
                                     ('Étape déclarée',self.phase,PHASES)]:
            tk.Label(fields,text=label,fg=MUTED,bg=PANEL).pack(anchor='w',pady=(5,2))
            ttk.Combobox(fields,textvariable=var,values=options,state='readonly').pack(fill='x',ipady=3)
        tk.Label(cont,text='Contrôles déclaratifs (jamais vérifiés automatiquement)',
                 fg=NEON,bg=DARK,font=('Segoe UI',11,'bold')).pack(anchor='w',pady=(13,6))
        checks = (
            ('Accès professionnel et habilitation nécessaires vérifiés',self.pro),
            ('Matériel / portail constructeur officiellement autorisé',self.device),
            ('Clé neuve ou pièce fournie par circuit conforme',self.part),
            ('Essais de fonctionnement effectués par le professionnel',self.test),
        )
        for label,var in checks:
            tk.Checkbutton(cont,text=label,variable=var,fg=INK,bg=DARK,activeforeground=INK,
                           activebackground=DARK,selectcolor=PANEL,wraplength=740,justify='left').pack(anchor='w')
        tk.Label(cont,text='Atelier partenaire / outil officiel (facultatif ; aucune donnée personnelle)',
                 fg=MUTED,bg=DARK).pack(anchor='w',pady=(12,3))
        tk.Entry(cont,textvariable=self.prestataire,font=('Segoe UI',11),bg='#f1f7fa',fg='#10263a').pack(fill='x',ipady=4)
        tk.Label(cont,text='Notes non sensibles (sans VIN, PIN, clé secrète, immatriculation ni identité)',
                 fg=MUTED,bg=DARK).pack(anchor='w',pady=(12,3))
        self.notes = tk.Text(cont,height=3,wrap='word',bg=PANEL,fg=INK,font=('Segoe UI',10))
        self.notes.pack(fill='x')
        self.notes.insert('1.0',self.record.note)
        buttons=tk.Frame(cont,bg=DARK)
        buttons.pack(fill='x',pady=(12,4))
        tk.Button(buttons,text='💾  Sauvegarder le suivi',command=self.save,bg=NEON,fg=DARK,
                  font=('Segoe UI',10,'bold'),padx=14,pady=10).pack(side='left',padx=(0,6))
        tk.Button(buttons,text='📄  Exporter le rapport',command=self.report,bg='#2b3d55',fg=INK,
                  padx=12,pady=10).pack(side='left',padx=(0,6))
        tk.Button(buttons,text='🔗  Site officiel SERMI',command=lambda:webbrowser.open('https://www.vehiclesermi.eu/'),
                  bg='#2b3d55',fg=INK,padx=12,pady=10).pack(side='left')
        tk.Label(cont,textvariable=self.status,fg=NEON,bg=DARK,wraplength=780,justify='left').pack(anchor='w',pady=6)
        tk.Label(cont,text=NOTICE,fg=WARNING,bg=DARK,wraplength=795,justify='left').pack(anchor='w',pady=(1,4))

    def gather(self) -> Replacement:
        return Replacement(dossier_id=self.case.id,type_cle=self.kind.get(),intervention=self.intervention.get(),
                           phase=self.phase.get(),controle_acces_professionnel=self.pro.get(),
                           outil_constructeur_agree=self.device.get(),provenance_cle_conforme=self.part.get(),
                           essais_declares=self.test.get(),prestataire=self.prestataire.get(),
                           note=self.notes.get('1.0','end').strip())

    def save(self):
        try:
            self.record=self.store.save(self.gather())
        except (OSError,ValueError,sqlite3.Error) as exc:
            messagebox.showerror('Intervention non enregistrée',str(exc),parent=self)
            return
        self.status.set('Enregistré localement ; aucune opération sur le véhicule. Les cases sont déclaratives.')

    def report(self):
        saved=self.store.get(self.case.id)
        if saved is None:
            messagebox.showinfo('Rapport','Sauvegarde d’abord le suivi.',parent=self)
            return
        # Ne jamais exporter des valeurs non sauvegardées en les faisant passer pour certifiées.
        unsaved=self.gather()
        fields=('type_cle','intervention','phase','controle_acces_professionnel','outil_constructeur_agree',
                'provenance_cle_conforme','essais_declares','prestataire','note')
        if any(getattr(saved,f)!=getattr(unsaved,f) for f in fields):
            messagebox.showinfo('Rapport','Sauvegarde tes modifications avant l’export.',parent=self)
            return
        dest=filedialog.asksaveasfilename(parent=self,defaultextension='.html',
                    initialfile=f'{saved.dossier_id}_remplacement.html',
                    filetypes=[('Document HTML','*.html')])
        if not dest:
            return
        try:
            Path(dest).write_text(report_html(saved,self.store.log(saved.dossier_id),
                                              self.case.marque,self.case.modele),encoding='utf-8')
            self.status.set('Rapport local exporté : '+Path(dest).name)
        except OSError as exc:
            messagebox.showerror('Export impossible',str(exc),parent=self)
