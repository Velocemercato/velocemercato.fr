# -*- coding: utf-8 -*-
"""VM Performance — suivi des interventions de clés automobiles autorisées.

AUCUNE action sur un véhicule, aucune programmation de clé / antidémarrage.
Aucune donnée d'identité, plaque ou VIN n'est demandée ou sauvegardée.
Copyright (C) 2026 VM Performance contributors; SPDX-License-Identifier: GPL-2.0-only
"""
from __future__ import annotations

import csv
import html
from contextlib import contextmanager, closing
import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, filedialog, ttk
import tkinter as tk

DARK = '#091120'
PANEL = '#111e31'
INK = '#eef6ff'
MUTED = '#b1bfd0'
NEON = '#37e4a5'
WARNING = '#ffcf6a'

ISSUES = (
    'Toutes les clés perdues', 'Clé cassée', 'Télécommande non fonctionnelle',
    'Batterie déchargée / diagnostic', 'Autre intervention',
)
STAGES = (
    'Demande reçue', 'Pièces et mandat vérifiés', 'Recherche de solution agréée',
    'Remplacement de clé en cours', 'Terminé — clé fonctionnelle', 'Annulé',
)

DISCLAIMER = (
    "Ce volet gère uniquement le dossier d'intervention. Il ne déverrouille pas, "
    "ne démarre pas et ne programme pas un véhicule. Une clé reconnue par "
    "le système constructeur (ou une réparation conforme) est nécessaire "
    "pour repartir. Vérifier identité, propriété/mandat et autorisations "
    "selon la réglementation et les procédures du professionnel."
)


def default_database() -> Path:
    base = os.environ.get('LOCALAPPDATA')
    folder = Path(base) / 'VMPerformance' if base else Path.home() / '.local' / 'share' / 'VMPerformance'
    return folder / 'dossiers_atelier.sqlite3'


def now_utc() -> str:
    return datetime.now().astimezone().isoformat(timespec='seconds')


def normalize_year(value: str) -> str:
    value = str(value).strip()
    if not value:
        return ''
    if not value.isdigit() or not 1950 <= int(value) <= datetime.now().year + 1:
        raise ValueError('Année non valide (1950 à année suivante).')
    return value


@dataclass
class Case:
    id: str = ''
    marque: str = ''
    modele: str = ''
    annee: str = ''
    motif: str = ISSUES[0]
    etape: str = STAGES[0]
    identite_propriete_verifiees: bool = False
    mandat_signe: bool = False
    notes: str = ''
    cree: str = ''
    maj: str = ''


def validate_case(case: Case) -> None:
    case.marque = case.marque.strip()
    case.modele = case.modele.strip()
    case.notes = case.notes.strip()
    case.annee = normalize_year(case.annee)
    if not (1 <= len(case.marque) <= 60):
        raise ValueError('Renseigner une marque (60 caractères maximum).')
    if not (1 <= len(case.modele) <= 80):
        raise ValueError('Renseigner un modèle (80 caractères maximum).')
    if len(case.notes) > 1200:
        raise ValueError('Notes trop longues (1200 caractères maximum).')
    if case.motif not in ISSUES:
        raise ValueError('Motif inconnu.')
    if case.etape not in STAGES:
        raise ValueError('Étape inconnue.')
    if case.etape not in (STAGES[0], STAGES[-1]):
        if not (case.identite_propriete_verifiees and case.mandat_signe):
            raise ValueError('Pour avancer : confirmer les justificatifs et le mandat signé.')


class CaseStore:
    def __init__(self, db_path: Path | None = None):
        self.db_path = Path(db_path) if db_path else default_database()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS dossiers (
                id TEXT PRIMARY KEY, marque TEXT NOT NULL, modele TEXT NOT NULL,
                annee TEXT NOT NULL, motif TEXT NOT NULL, etape TEXT NOT NULL,
                identite_propriete_verifiees INTEGER NOT NULL, mandat_signe INTEGER NOT NULL,
                notes TEXT NOT NULL, cree TEXT NOT NULL, maj TEXT NOT NULL
            )''')

    @contextmanager
    def _connect(self):
        """Close SQLite connections after committing or rolling back each operation."""
        with closing(sqlite3.connect(str(self.db_path), timeout=5)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")
            with conn:
                yield conn

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Case:
        data = dict(row)
        data['identite_propriete_verifiees'] = bool(data['identite_propriete_verifiees'])
        data['mandat_signe'] = bool(data['mandat_signe'])
        return Case(**data)

    def save(self, case: Case) -> Case:
        validate_case(case)
        if not case.id:
            case.id = 'VM-' + uuid.uuid4().hex[:10].upper()
            case.cree = now_utc()
        case.maj = now_utc()
        with self._connect() as conn:
            conn.execute('''INSERT INTO dossiers
              (id,marque,modele,annee,motif,etape,identite_propriete_verifiees,
               mandat_signe,notes,cree,maj)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
               marque=excluded.marque, modele=excluded.modele,
               annee=excluded.annee, motif=excluded.motif, etape=excluded.etape,
               identite_propriete_verifiees=excluded.identite_propriete_verifiees,
               mandat_signe=excluded.mandat_signe, notes=excluded.notes,
               maj=excluded.maj''', (
                case.id, case.marque, case.modele, case.annee, case.motif, case.etape,
                int(case.identite_propriete_verifiees), int(case.mandat_signe),
                case.notes, case.cree, case.maj,
            ))
        return case

    def get(self, case_id: str) -> Case | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM dossiers WHERE id=?', (case_id,)).fetchone()
        return self._from_row(row) if row else None

    def list(self) -> list[Case]:
        with self._connect() as conn:
            rows = conn.execute('SELECT * FROM dossiers ORDER BY maj DESC, id DESC').fetchall()
        return [self._from_row(row) for row in rows]

    def delete(self, case_id: str):
        with self._connect() as conn:
            conn.execute('DELETE FROM dossiers WHERE id=?', (case_id,))


def to_html(case: Case) -> str:
    """Rapport local imprimable, sans photos ni données personnelles."""
    esc = lambda v: html.escape(str(v), quote=True)
    def row(key, val):
        return f'<tr><th>{esc(key)}</th><td>{esc(val)}</td></tr>'
    items = (
        ('Dossier', case.id), ('Marque', case.marque), ('Modèle', case.modele),
        ('Année', case.annee or 'Non précisée'), ('Motif', case.motif),
        ('Étape', case.etape),
        ('Justificatifs vus par le professionnel', 'Déclaré vérifié' if case.identite_propriete_verifiees else 'Non vérifié'),
        ('Mandat signé', 'Déclaré vérifié' if case.mandat_signe else 'Non vérifié'),
        ('Notes techniques sans données personnelles', case.notes),
        ('Créé', case.cree), ('Dernière mise à jour', case.maj),
    )
    return '''<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>VM Performance — Fiche atelier</title>
<style>body{font-family:Arial,sans-serif;max-width:760px;margin:36px auto;padding:0 18px;color:#132238}
h1{border-bottom:4px solid #17a676;padding-bottom:12px}table{border-collapse:collapse;width:100%;margin-top:24px}
th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #cdd8dd;white-space:pre-wrap;overflow-wrap:anywhere}
th{width:36%;background:#eef6f3}p{line-height:1.5}.warn{background:#fff4d5;padding:14px;border-left:5px solid #d2a340}
@media print{body{margin:0}.warn{break-inside:avoid}}</style></head><body>
<h1>VM PERFORMANCE — FICHE ATELIER</h1><p>Diagnostic / suivi client · Fiche de gestion uniquement</p>
<table>''' + ''.join(row(k, v) for k, v in items) + '''</table>
<p class="warn">''' + esc(DISCLAIMER) + '''</p>
<p><small>Généré localement — aucun envoi automatique</small></p></body></html>'''


def csv_safe(value) -> str:
    """Neutralise spreadsheet formulas in exported untrusted text fields."""
    value = str(value)
    # Excel and similar spreadsheet apps may evaluate formula-like cell content.
    if value.lstrip(' \t\r\n').startswith(('=', '+', '-', '@')) or value[:1] in ('\t', '\r', '\n'):
        return "'" + value
    return value


def export_csv(cases: list[Case], path: Path):
    with Path(path).open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Réf.', 'Marque', 'Modèle', 'Année', 'Motif', 'Étape',
                         'Justificatifs vérifiés (déclaration)', 'Mandat signé (déclaration)',
                         'Créé', 'Mis à jour'])
        for c in cases:
            writer.writerow([csv_safe(v) for v in (
                c.id, c.marque, c.modele, c.annee, c.motif, c.etape,
                'Oui' if c.identite_propriete_verifiees else 'Non',
                'Oui' if c.mandat_signe else 'Non', c.cree, c.maj)])


class DossiersWindow(tk.Toplevel):
    """Volet administratif : aucune interface de démarrage ou accès véhicule."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title('VM Performance — Gestion des interventions clés')
        self.geometry('1080x770')
        self.minsize(860, 610)
        self.configure(bg=DARK)
        self.store = CaseStore()
        self.current_id = ''
        self.vars = {k: tk.StringVar() for k in ('marque', 'modele', 'annee')}
        self.motif = tk.StringVar(value=ISSUES[0])
        self.etape = tk.StringVar(value=STAGES[0])
        self.verifie = tk.BooleanVar(value=False)
        self.mandat = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value='Dossiers sauvegardés uniquement sur cet ordinateur.')
        self._build()
        self.refresh_list()

    def _label(self, parent, text, color=MUTED):
        return tk.Label(parent, text=text, bg=parent.cget('bg'), fg=color,
                        font=('Segoe UI', 10), anchor='w', justify='left')

    def _button(self, parent, name, command, accent=False):
        return tk.Button(parent, text=name, command=command, bg=NEON if accent else '#2b3d55',
                         fg=DARK if accent else INK, activebackground=WARNING,
                         borderwidth=0, relief='flat', cursor='hand2', padx=13,
                         pady=9, font=('Segoe UI', 10, 'bold'))

    def _build(self):
        title = tk.Frame(self, bg=DARK, padx=20, pady=14)
        title.pack(fill='x')
        self._label(title, 'VM  /  ATELIER CLÉS', NEON).pack(anchor='w')
        self._label(title, 'Suivi professionnel des demandes — aucun déverrouillage ou démarrage de véhicule', INK).pack(anchor='w')
        split = tk.Frame(self, bg=DARK, padx=18)
        split.pack(fill='both', expand=True)
        left = tk.Frame(split, bg=PANEL, padx=12, pady=12)
        left.pack(side='left', fill='y', padx=(0, 12))
        self._label(left, 'DOSSIERS').pack(anchor='w')
        self.case_list = tk.Listbox(left, bg='#0b1727', fg=INK, selectbackground='#2c755f',
                                    borderwidth=0, font=('Consolas', 10), width=35, height=20)
        self.case_list.pack(fill='both', expand=True, pady=(10, 9))
        self.case_list.bind('<<ListboxSelect>>', self.select_case)
        self._button(left, '＋ Nouveau dossier', self.new_case, True).pack(fill='x', pady=3)
        self._button(left, 'Exporter la liste CSV', self.export_all).pack(fill='x', pady=3)
        self._button(left, 'Supprimer sélection', self.delete_case).pack(fill='x', pady=3)
        right = tk.Frame(split, bg=PANEL, padx=18, pady=14)
        right.pack(side='right', fill='both', expand=True)
        self._label(right, 'FICHE D’INTERVENTION', INK).pack(anchor='w')
        self.ref = self._label(right, 'Nouvelle fiche')
        self.ref.pack(anchor='w', pady=(3, 12))
        grid = tk.Frame(right, bg=PANEL)
        grid.pack(fill='x')
        for r, (key, prompt) in enumerate([('marque', 'Marque (ex. Renault)'),
                                          ('modele', 'Modèle (ex. Clio)'),
                                          ('annee', 'Année (facultative)')]):
            self._label(grid, prompt).grid(row=r, column=0, sticky='w', pady=5)
            e = tk.Entry(grid, textvariable=self.vars[key], bg='#f0f6fd', fg='#132238', relief='flat', font=('Segoe UI', 11))
            e.grid(row=r, column=1, sticky='ew', padx=(16, 0), pady=5, ipady=6)
        grid.grid_columnconfigure(1, weight=1)
        self._label(right, 'Motif').pack(anchor='w', pady=(9, 3))
        ttk.Combobox(right, textvariable=self.motif, state='readonly', values=ISSUES).pack(fill='x')
        self._label(right, 'Avancement').pack(anchor='w', pady=(9, 3))
        ttk.Combobox(right, textvariable=self.etape, state='readonly', values=STAGES).pack(fill='x')
        tk.Checkbutton(right, text='Je confirme avoir vérifié identité et propriété / mandat du véhicule',
                       variable=self.verifie, bg=PANEL, fg=INK, selectcolor='#203a3a', activebackground=PANEL,
                       activeforeground=INK, wraplength=550, justify='left').pack(anchor='w', pady=(14, 1))
        tk.Checkbutton(right, text='Je confirme disposer de l’autorisation écrite d’intervention',
                       variable=self.mandat, bg=PANEL, fg=INK, selectcolor='#203a3a', activebackground=PANEL,
                       activeforeground=INK, wraplength=550, justify='left').pack(anchor='w', pady=(1, 9))
        self._label(right, 'Notes techniques (aucun nom, téléphone, plaque, VIN ou pièce d’identité)').pack(anchor='w')
        self.notes = tk.Text(right, height=5, wrap='word', bg='#0b1727', fg=INK, relief='flat', font=('Segoe UI', 10))
        self.notes.pack(fill='both', expand=True, pady=(5, 10))
        buttons = tk.Frame(right, bg=PANEL)
        buttons.pack(fill='x')
        self._button(buttons, 'Enregistrer la fiche', self.save_case, True).pack(side='left', padx=(0, 8))
        self._button(buttons, 'Rapport HTML imprimable', self.export_report).pack(side='left')
        self._button(right, '🔐  Remplacement / programmation agréée (suivi)', self.open_replacement, True).pack(fill='x', pady=(9, 0))
        footer = tk.Frame(self, bg=DARK, padx=20, pady=10)
        footer.pack(fill='x')
        self._label(footer, DISCLAIMER, WARNING).pack(anchor='w', fill='x')
        tk.Label(footer, textvariable=self.status, bg=DARK, fg=NEON,
                 anchor='w', wraplength=940).pack(anchor='w', pady=(8, 0))

    def open_replacement(self):
        """Ouvre un suivi administratif lié au dossier enregistré.

        Ne communique jamais avec les modules antivol, clés ou ECU.
        """
        if not self.current_id or self.store.get(self.current_id) is None:
            messagebox.showinfo('Dossier requis', 'Enregistre d’abord le dossier de clé.', parent=self)
            return
        try:
            from remplacement_cles import ReplacementWindow
            w = ReplacementWindow(self, self.store, self.current_id)
            w.transient(self)
        except (OSError, sqlite3.Error, ValueError) as exc:
            messagebox.showerror('Suivi de remplacement', str(exc), parent=self)

    def gather(self) -> Case:
        original = self.store.get(self.current_id) if self.current_id else None
        return Case(id=self.current_id, cree=original.cree if original else '',
                    marque=self.vars['marque'].get(), modele=self.vars['modele'].get(),
                    annee=self.vars['annee'].get(), motif=self.motif.get(),
                    etape=self.etape.get(), identite_propriete_verifiees=self.verifie.get(),
                    mandat_signe=self.mandat.get(), notes=self.notes.get('1.0', 'end').strip())

    def save_case(self):
        try:
            c = self.store.save(self.gather())
        except (ValueError, OSError, sqlite3.Error) as e:
            messagebox.showerror('Fiche à corriger', str(e), parent=self)
            return
        self.current_id = c.id
        self.ref.config(text=c.id)
        self.refresh_list()
        self.status.set(f'{c.id} : fiche enregistrée localement. Justificatifs NON sauvegardés ici.')

    def refresh_list(self):
        self.case_list.delete(0, 'end')
        self.case_ids = []
        for c in self.store.list():
            self.case_ids.append(c.id)
            self.case_list.insert('end', f'{c.id[-6:]}  {c.marque[:11]:11} {c.modele[:13]}')

    def select_case(self, event=None):
        ix = self.case_list.curselection()
        if not ix or ix[0] >= len(self.case_ids):
            return
        c = self.store.get(self.case_ids[ix[0]])
        if c is None:
            return
        self.current_id = c.id
        self.ref.config(text=f'{c.id} · Créé {c.cree}')
        for key in self.vars:
            self.vars[key].set(getattr(c, key))
        self.motif.set(c.motif)
        self.etape.set(c.etape)
        self.verifie.set(c.identite_propriete_verifiees)
        self.mandat.set(c.mandat_signe)
        self.notes.delete('1.0', 'end')
        self.notes.insert('1.0', c.notes)

    def new_case(self):
        self.current_id = ''
        self.ref.config(text='Nouvelle fiche')
        for var in self.vars.values():
            var.set('')
        self.motif.set(ISSUES[0]); self.etape.set(STAGES[0])
        self.verifie.set(False); self.mandat.set(False)
        self.notes.delete('1.0', 'end')
        self.case_list.selection_clear(0, 'end')

    def delete_case(self):
        if not self.current_id:
            messagebox.showinfo('Sélection', 'Sélectionne une fiche enregistrée.', parent=self)
            return
        if not messagebox.askyesno('Supprimer définitivement', f'Supprimer {self.current_id} ?', parent=self):
            return
        self.store.delete(self.current_id)
        self.new_case(); self.refresh_list()
        self.status.set('Fiche supprimée de la base locale.')

    def export_report(self):
        try:
            c = self.gather()
            if not c.id:
                messagebox.showinfo('Rapport', 'Enregistre la fiche avant de faire un rapport.', parent=self)
                return
            validate_case(c)
            dest = filedialog.asksaveasfilename(parent=self, title='Exporter la fiche atelier',
                        defaultextension='.html', initialfile=f'{c.id}.html',
                        filetypes=[('Page imprimable', '*.html')])
            if not dest:
                return
            # Rapport fondé sur la fiche enregistrée, évite toute discordance avec les champs non sauvegardés.
            saved = self.store.get(c.id)
            if saved is None:
                raise ValueError('Fiche non trouvée.')
            if saved != c and (saved.marque, saved.modele, saved.annee, saved.motif, saved.etape,
                saved.identite_propriete_verifiees, saved.mandat_signe, saved.notes) != (
                c.marque,c.modele,c.annee,c.motif,c.etape,c.identite_propriete_verifiees,c.mandat_signe,c.notes):
                raise ValueError('Les champs ont changé : enregistre avant d’exporter.')
            Path(dest).write_text(to_html(saved), encoding='utf-8')
            self.status.set(f'Fiche HTML exportée : {Path(dest).name}')
        except (ValueError, OSError, sqlite3.Error) as e:
            messagebox.showerror('Export', str(e), parent=self)

    def export_all(self):
        cases = self.store.list()
        if not cases:
            messagebox.showinfo('Export', 'Aucun dossier à exporter.', parent=self)
            return
        dest = filedialog.asksaveasfilename(parent=self, title='Export liste dossiers',
                    defaultextension='.csv', initialfile='VM_interventions.csv',
                    filetypes=[('CSV', '*.csv')])
        if dest:
            try:
                export_csv(cases, Path(dest))
                self.status.set(f'{len(cases)} dossier(s) exporté(s) en CSV.')
            except OSError as e:
                messagebox.showerror('Export CSV', str(e), parent=self)
